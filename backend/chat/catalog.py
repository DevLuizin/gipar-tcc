# -*- coding: utf-8 -*-
"""
Catálogo de Equipamentos e Extrator de Entidades com RapidFuzz — GIPAR Chatbot
Responsável pela identificação de itens aproximados (tolerância a erros) e
desambiguação proativa de termos genéricos (RN-008).
"""

import re
import unicodedata
from typing import List, Dict, Optional, Tuple
from rapidfuzz import fuzz, process

def normalize_name(text: str) -> str:
    """Normaliza texto para comparação: minúsculas, sem acentos e sem pontuação."""
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return " ".join(text.split())

STOPWORDS_QUERY = {
    "tem", "temos", "voce", "voces", "algum", "alguma", "qual", "quais",
    "disponivel", "disponiveis", "livre", "livres", "sobrando", "estoque",
    "laboratorio", "lab", "bancada", "pra", "para", "de", "do", "da", "dos",
    "das", "o", "a", "os", "as", "um", "uma", "uns", "umas", "onde", "fica",
    "estao", "esta", "pegar", "usar", "retirar", "posso", "favor", "por",
    "nós", "nos", "aqui"
}

def clean_query_tokens(query: str) -> str:
    """Remove palavras comuns de pergunta para destacar o nome do equipamento."""
    norm = normalize_name(query)
    words = [w for w in norm.split() if w not in STOPWORDS_QUERY]
    return " ".join(words) if words else norm

class EquipmentCatalog:
    def __init__(self, items: Optional[List[Dict]] = None):
        self.items: List[Dict] = []
        self.normalized_map: List[Tuple[str, Dict]] = []
        if items:
            self.set_items(items)

    def set_items(self, items: List[Dict]) -> None:
        """Atualiza a lista de itens do catálogo e prepara índices normalizados."""
        self.items = items
        self.normalized_map = []
        for it in items:
            raw_name = it.get("nome", "")
            norm_name = normalize_name(raw_name)
            self.normalized_map.append((norm_name, it))

    def find_matches(self, user_query: str, threshold: float = 75.0) -> List[Tuple[Dict, float]]:
        """
        Localiza todos os itens que correspondem à pergunta com score >= threshold.
        Utiliza token_set_ratio para tolerar palavras extras na pergunta.
        """
        if not self.normalized_map:
            return []

        cleaned_query = clean_query_tokens(user_query)
        target_query = cleaned_query if len(cleaned_query) >= 3 else normalize_name(user_query)

        scored_matches: List[Tuple[Dict, float]] = []

        for norm_name, item in self.normalized_map:
            if target_query == norm_name:
                best_score = 100.0
            else:
                score_sort = fuzz.token_sort_ratio(target_query, norm_name)
                score_set = fuzz.token_set_ratio(target_query, norm_name)
                score_partial = fuzz.partial_ratio(target_query, norm_name)
                
                # Se for termo genérico curto (1 palavra como 'jumper' ou 'arduino') contido no nome
                if len(target_query.split()) == 1 and len(target_query) >= 4 and target_query in norm_name:
                    best_score = max(score_set, 90.0)
                else:
                    best_score = max(score_sort, (score_set * 0.85), (score_partial * 0.8))

            if best_score >= threshold:
                scored_matches.append((item, round(best_score, 1)))

        # Ordena pelo maior score e depois pelo nome
        scored_matches.sort(key=lambda x: (x[1], x[0].get("nome", "")), reverse=True)
        return scored_matches

    def match_item(self, user_query: str, threshold: float = 75.0) -> Tuple[Optional[Dict], List[Dict], float]:
        """
        Analisa a consulta e retorna:
        - (item_unico, [], score) se houver um match claro ou dominante;
        - (None, lista_itens, score) se for termo genérico com múltiplas opções para desambiguação (RN-008);
        - (None, [], 0.0) se nenhum item atingir o limiar (RN-010).
        """
        matches = self.find_matches(user_query, threshold=threshold)
        if not matches:
            return (None, [], 0.0)

        # Se houver apenas um match
        if len(matches) == 1:
            return (matches[0][0], [], matches[0][1])

        top_item, top_score = matches[0]
        second_item, second_score = matches[1]

        cleaned = clean_query_tokens(user_query)
        is_generic_term = len(cleaned.split()) <= 1

        # Verifica se o primeiro item é uma correspondência exata do nome
        is_exact_name = (normalize_name(top_item.get("nome", "")) == cleaned)

        # 1. Se for match exato de nome composto (ex: 'arduino uno' ou 'cabo mini usb')
        if is_exact_name and not is_generic_term:
            return (top_item, [], 100.0)

        # 2. Se a busca é genérica (1 palavra como 'jumper' ou 'arduino') com múltiplos itens no catálogo
        if is_generic_term and len(matches) > 1:
            disambiguation_list = [m[0] for m in matches[:5]]
            return (None, disambiguation_list, top_score)

        # 3. Se não é termo genérico e o top score supera o segundo com folga
        if not is_generic_term and top_score >= 88.0 and (top_score - second_score >= 10.0):
            return (top_item, [], top_score)

        # 4. Caso contrário, desambigua
        disambiguation_list = [m[0] for m in matches[:5]]
        return (None, disambiguation_list, top_score)

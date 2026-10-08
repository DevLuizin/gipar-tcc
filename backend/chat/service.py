# -*- coding: utf-8 -*-
"""
Serviço Orquestrador do Chatbot — GIPAR
Integra o pipeline de NLP (Scikit-Learn), o catálogo fuzzy (RapidFuzz),
as regras parametrizadas (lab_rules.json) e as respostas objetivas (RN-008, RN-009, RN-010, RN-011).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .pipeline import ChatNLPPipeline
from .catalog import EquipmentCatalog, clean_query_tokens

CURRENT_DIR = Path(__file__).resolve().parent
RULES_PATH = CURRENT_DIR / "lab_rules.json"

class ChatbotService:
    def __init__(
        self,
        pipeline: Optional[ChatNLPPipeline] = None,
        catalog: Optional[EquipmentCatalog] = None,
        rules_path: Optional[Path] = None
    ):
        self.pipeline = pipeline or ChatNLPPipeline()
        self.catalog = catalog or EquipmentCatalog()
        self.rules_path = Path(rules_path) if rules_path else RULES_PATH
        self.rules: Dict = {}
        self.load_rules()

    def load_rules(self) -> None:
        """Carrega regras de funcionamento e empréstimo do lab_rules.json (RN-011)."""
        if self.rules_path.exists():
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.rules = json.load(f)
            except Exception:
                self.rules = {}

    def reload(self, items: Optional[List[Dict]] = None) -> None:
        """Recarrega o pipeline de NLP, as regras e atualiza os itens do catálogo."""
        self.pipeline.reload()
        self.load_rules()
        if items is not None:
            self.catalog.set_items(items)

    def process_message(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Processa a mensagem do aluno e devolve a resposta contextual estruturada:
        {
            "reply": str,
            "intent": str,
            "confidence": float,
            "matched_item": Optional[Dict],
            "options": Optional[List[Dict]]
        }
        """
        if not message or not message.strip():
            return {
                "reply": "Olá! Como posso ajudar com os equipamentos do laboratório?",
                "intent": "saudacao",
                "confidence": 1.0,
                "matched_item": None,
                "options": None
            }

        text = message.strip()
        intent, confidence = self.pipeline.predict_intent(text)

        # 1. Saudação
        if intent == "saudacao":
            static_reply = self.pipeline.get_static_response("saudacao") or "Olá! Como posso ajudar com os equipamentos do laboratório hoje?"
            return {
                "reply": static_reply,
                "intent": intent,
                "confidence": confidence,
                "matched_item": None,
                "options": None
            }

        # 2. Despedida
        if intent == "despedida":
            static_reply = self.pipeline.get_static_response("despedida") or "De nada! Bons estudos e boas montagens no laboratório."
            return {
                "reply": static_reply,
                "intent": intent,
                "confidence": confidence,
                "matched_item": None,
                "options": None
            }

        # 3. Ajuda
        if intent == "ajuda":
            static_reply = self.pipeline.get_static_response("ajuda")
            return {
                "reply": static_reply,
                "intent": intent,
                "confidence": confidence,
                "matched_item": None,
                "options": None
            }

        # 4. Horário de Funcionamento (RN-011)
        if intent == "horario_funcionamento":
            horario_info = self.rules.get("horario_funcionamento", {})
            msg = horario_info.get(
                "mensagem",
                "O laboratório funciona de Segunda a Sexta, das 08h às 18h. As devoluções de material de bancada devem ser feitas até 15 minutos antes do fechamento."
            )
            return {
                "reply": msg,
                "intent": intent,
                "confidence": confidence,
                "matched_item": None,
                "options": None
            }

        # 5. Regras de Empréstimo (RN-011)
        if intent == "regras_emprestimo":
            regras_info = self.rules.get("regras_emprestimo", {})
            bancada = regras_info.get("bancada", {}).get("descricao", "Componentes de bancada são para uso no mesmo dia.")
            externo = regras_info.get("externo_projetos", {}).get("descricao", "Kits para TCC/projetos podem ser emprestados por até 7 dias mediante autorização.")
            full_reply = f"{bancada}\n\nPara projetos/TCC: {externo}"
            return {
                "reply": full_reply,
                "intent": intent,
                "confidence": confidence,
                "matched_item": None,
                "options": None
            }

        # 6. Consultas de Itens (Disponibilidade ou Localização)
        if intent in ("consultar_disponibilidade", "consultar_localizacao", "desconhecido"):
            single_item, multi_items, match_score = self.catalog.match_item(text, threshold=75.0)

            # Caso 6.1: Nenhum item localizado (RN-010)
            if not single_item and not multi_items:
                # Se não localizou item e a intenção é desconhecida, oferecer ajuda
                if intent == "desconhecido":
                    return {
                        "reply": "Não compreendi sua solicitação. Posso te ajudar com a disponibilidade de componentes, regras de empréstimo ou horários do laboratório.",
                        "intent": "desconhecido",
                        "confidence": confidence,
                        "matched_item": None,
                        "options": None
                    }
                # Se era pergunta de item, resposta estrita RN-010
                return {
                    "reply": "Item não cadastrado no acervo.",
                    "intent": intent,
                    "confidence": confidence,
                    "matched_item": None,
                    "options": None
                }

            # Caso 6.2: Múltiplos itens encontrados -> Desambiguação Proativa (RN-008)
            if multi_items:
                term = clean_query_tokens(text) or "itens"
                lines = [f"Temos as seguintes opções de '{term}' no acervo:"]
                for it in multi_items:
                    nome = it.get("nome", "Item")
                    status = str(it.get("status", "")).upper()
                    qtd = it.get("quantidade", 0)
                    if status == "DISPONIVEL" and qtd > 0:
                        lines.append(f"- {nome}: {qtd} unidades disponíveis")
                    else:
                        lines.append(f"- {nome}: Indisponível no momento")
                lines.append("\nQual dessas opções você precisa?")

                return {
                    "reply": "\n".join(lines),
                    "intent": "consultar_disponibilidade",
                    "confidence": confidence,
                    "matched_item": None,
                    "options": multi_items
                }

            # Caso 6.3: Item único identificado
            if single_item:
                nome = single_item.get("nome", "Equipamento")
                status = str(single_item.get("status", "")).upper()
                qtd = single_item.get("quantidade", 0)
                modelo = single_item.get("modelo") or ""

                # Verificar se está disponível (RN-009 / RN-010)
                if status != "DISPONIVEL" or qtd <= 0:
                    return {
                        "reply": "Item indisponível no momento.",
                        "intent": intent,
                        "confidence": confidence,
                        "matched_item": single_item,
                        "options": None
                    }

                # Se a intenção for localização física
                if intent == "consultar_localizacao":
                    local_padrao = "Armário Geral do Laboratório"
                    return {
                        "reply": f"O item '{nome}' está localizado no {local_padrao} ({qtd} unidades disponíveis).",
                        "intent": intent,
                        "confidence": confidence,
                        "matched_item": single_item,
                        "options": None
                    }

                # Resposta padrão de disponibilidade (RN-009)
                reply = f"Sim! Temos {qtd} unidades de '{nome}' disponíveis no laboratório."
                return {
                    "reply": reply,
                    "intent": "consultar_disponibilidade",
                    "confidence": confidence,
                    "matched_item": single_item,
                    "options": None
                }

        # Fallback padrão
        return {
            "reply": "Não compreendi sua solicitação. Posso te ajudar com a disponibilidade de componentes, regras de empréstimo ou horários do laboratório.",
            "intent": "desconhecido",
            "confidence": confidence,
            "matched_item": None,
            "options": None
        }

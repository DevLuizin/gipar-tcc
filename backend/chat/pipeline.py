# -*- coding: utf-8 -*-
"""
Motor de Classificação de Intenções — GIPAR Chatbot
Utiliza Scikit-Learn (TF-IDF + Regressão Logística) para treinamento em memória
e inferência ultra-rápida (<10ms).
"""

import os
import json
import random
import unicodedata
from pathlib import Path
from typing import Tuple, Optional, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

CURRENT_DIR = Path(__file__).resolve().parent
DEFAULT_INTENTS_PATH = CURRENT_DIR / "intents.json"

def normalize_text(text: str) -> str:
    """Remove acentos, converte para minúsculas e remove espaços extras."""
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text

class ChatNLPPipeline:
    def __init__(self, intents_path: Optional[Path] = None):
        self.intents_path = Path(intents_path) if intents_path else DEFAULT_INTENTS_PATH
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            analyzer="word",
            preprocessor=normalize_text,
            sublinear_tf=True
        )
        self.classifier = LogisticRegression(
            max_iter=1000,
            C=1.5,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42
        )
        self.intents_data: Dict = {}
        self.tags: List[str] = []
        self.is_trained: bool = False
        self.train()

    def train(self) -> None:
        """Carrega intents.json e treina o modelo em memória."""
        if not self.intents_path.exists():
            raise FileNotFoundError(f"Arquivo de intenções não encontrado: {self.intents_path}")

        with open(self.intents_path, "r", encoding="utf-8") as f:
            self.intents_data = json.load(f)

        patterns: List[str] = []
        labels: List[str] = []

        for item in self.intents_data.get("intents", []):
            tag = item["tag"]
            for pat in item.get("patterns", []):
                patterns.append(pat)
                labels.append(tag)

        if not patterns:
            raise ValueError("O dataset de intenções está vazio.")

        X = self.vectorizer.fit_transform(patterns)
        self.classifier.fit(X, labels)
        self.tags = list(self.classifier.classes_)
        self.is_trained = True

    def predict_intent(self, text: str, threshold: float = 0.22) -> Tuple[str, float]:
        """
        Classifica a intenção da mensagem.
        Retorna uma tupla (intent_tag, confidence_score).
        Se a confiança for inferior ao threshold, retorna ('desconhecido', confidence).
        """
        if not self.is_trained or not text or not text.strip():
            return ("desconhecido", 0.0)

        vec = self.vectorizer.transform([text])
        probabilities = self.classifier.predict_proba(vec)[0]
        max_idx = probabilities.argmax()
        confidence = float(probabilities[max_idx])
        tag = self.tags[max_idx]

        if confidence < threshold:
            return ("desconhecido", confidence)

        return (tag, confidence)

    def get_static_response(self, tag: str) -> Optional[str]:
        """Retorna uma resposta estática aleatória associada à tag, se houver."""
        for item in self.intents_data.get("intents", []):
            if item["tag"] == tag:
                responses = item.get("responses", [])
                if responses:
                    return random.choice(responses)
        return None

    def reload(self) -> None:
        """Recarrega intents.json e retreina o pipeline em memória."""
        self.train()

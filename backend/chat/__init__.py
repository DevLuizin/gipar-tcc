# Módulo de Chatbot Inteligente — GIPAR
"""
Pacote responsável pelo processamento de linguagem natural (NLP),
classificação de intenções, extração de entidades aproximadas (RapidFuzz)
e consultas dinâmicas de patrimônio.
"""

from .pipeline import ChatNLPPipeline
from .catalog import EquipmentCatalog
from .service import ChatbotService

__all__ = ["ChatNLPPipeline", "EquipmentCatalog", "ChatbotService"]

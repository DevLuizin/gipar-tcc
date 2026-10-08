# -*- coding: utf-8 -*-
"""
Router FastAPI para o Módulo de Chatbot — GIPAR
Rotas:
- POST /api/chat: processa mensagens em linguagem natural.
- POST /api/chat/reload: recarrega regras e itens do banco sem reiniciar o container.
"""

import os
import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from .service import ChatbotService
from .pipeline import ChatNLPPipeline
from .catalog import EquipmentCatalog

router = APIRouter(tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem enviada pelo usuário")

class ChatResponse(BaseModel):
    reply: str
    intent: str
    confidence: float
    matched_item: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, Any]]] = None

# Instância singleton do serviço de chatbot
chat_service = ChatbotService()

def get_db_config() -> dict:
    return {
        "host": os.getenv("host") or os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("user") or os.getenv("DB_USER", "root"),
        "password": os.getenv("password") if os.getenv("password") is not None else os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("database") or os.getenv("DB_NAME", "gipar_db"),
        "cursorclass": DictCursor
    }

def fetch_catalog_items_from_db() -> List[Dict]:
    """Consulta os equipamentos ativos no banco de dados MySQL."""
    cfg = get_db_config()
    items = []
    con = None
    try:
        con = pymysql.connect(**cfg)
        with con.cursor() as cur:
            sql = """
                SELECT id, codigo_patrimonio, nome, modelo, status, quantidade, ativo
                FROM equipamento
                WHERE ativo = 1
            """
            cur.execute(sql)
            items = cur.fetchall() or []
    except Exception as e:
        print(f"[Chatbot] Aviso: Erro ao carregar itens do MySQL: {e}")
    finally:
        if con:
            con.close()
    return items

def initialize_chatbot() -> None:
    """Carrega o catálogo inicial a partir do MySQL."""
    items = fetch_catalog_items_from_db()
    if items:
        chat_service.catalog.set_items(items)
        print(f"[Chatbot] Catálogo inicializado com {len(items)} equipamentos.")
    else:
        print("[Chatbot] Nenhum item carregado do banco de dados na inicialização.")

# Inicializa o catálogo na importação
initialize_chatbot()

@router.post("/chat", response_model=ChatResponse, summary="Conversar com o Chatbot do laboratório")
async def chat_interaction(req: ChatRequest):
    """
    Processa uma mensagem do usuário e devolve a resposta contextual:
    - Identificação de intenções (saudação, disponibilidade, regras, etc.);
    - Extração fuzzy de equipamentos com tolerância a erros;
    - Desambiguação proativa para termos genéricos (RN-008);
    - Respostas estritas e objetivas (RN-009, RN-010).
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="A mensagem não pode ser vazia.")

    # Se o catálogo estiver vazio, tenta carregar novamente do banco
    if not chat_service.catalog.items:
        items = fetch_catalog_items_from_db()
        if items:
            chat_service.catalog.set_items(items)

    result = chat_service.process_message(req.message)
    return ChatResponse(**result)

@router.post("/chat/reload", summary="Recarregar modelo NLP, regras e acervo do banco")
async def reload_chatbot():
    """Recarrega intents.json, lab_rules.json e o acervo do MySQL em tempo de execução."""
    items = fetch_catalog_items_from_db()
    chat_service.reload(items=items)
    return {
        "status": "ok",
        "message": "Chatbot recarregado com sucesso.",
        "items_count": len(items)
    }

# -*- coding: utf-8 -*-
"""
Testes Automatizados da Fase 1 — Pipeline NLP e Catálogo do Chatbot GIPAR
Valida acurácia de intenções, fuzzy matching, desambiguação e regras RN-008 a RN-011.
"""

import pytest
try:
    from chat.pipeline import ChatNLPPipeline
    from chat.catalog import EquipmentCatalog
    from chat.service import ChatbotService
except ImportError:
    from backend.chat.pipeline import ChatNLPPipeline
    from backend.chat.catalog import EquipmentCatalog
    from backend.chat.service import ChatbotService


# Amostra realista baseada no banco MySQL do GIPAR
MOCK_ITEMS = [
    {"id": 1, "codigo_patrimonio": "0001", "nome": "jumper femea x femea", "status": "DISPONIVEL", "quantidade": 950},
    {"id": 2, "codigo_patrimonio": "0002", "nome": "jumper macho x femea", "status": "DISPONIVEL", "quantidade": 1},
    {"id": 3, "codigo_patrimonio": "0003", "nome": "jumper macho x macho", "status": "DISPONIVEL", "quantidade": 165},
    {"id": 6, "codigo_patrimonio": "0006", "nome": "Cabo arduino", "status": "DISPONIVEL", "quantidade": 83},
    {"id": 7, "codigo_patrimonio": "0007", "nome": "Cabo Mini USB", "status": "DISPONIVEL", "quantidade": 5},
    {"id": 8, "codigo_patrimonio": "0008", "nome": "Placa perfurada", "status": "DISPONIVEL", "quantidade": 13},
    {"id": 9, "codigo_patrimonio": "0009", "nome": "Placa de fenolite", "status": "MANUTENCAO", "quantidade": 0},
    {"id": 10, "codigo_patrimonio": "0010", "nome": "Ponte H L298N", "status": "DISPONIVEL", "quantidade": 23},
    {"id": 11, "codigo_patrimonio": "0011", "nome": "Arduino mega2560", "status": "DISPONIVEL", "quantidade": 42},
    {"id": 12, "codigo_patrimonio": "0012", "nome": "Arduino uno", "status": "DISPONIVEL", "quantidade": 6},
    {"id": 14, "codigo_patrimonio": "0014", "nome": "Modulo relé 8", "status": "DISPONIVEL", "quantidade": 10},
    {"id": 20, "codigo_patrimonio": "0020", "nome": "Osciloscópio Digital", "status": "DISPONIVEL", "quantidade": 2}
]

@pytest.fixture(scope="module")
def nlp_pipeline():
    return ChatNLPPipeline()

@pytest.fixture(scope="module")
def catalog():
    return EquipmentCatalog(items=MOCK_ITEMS)

@pytest.fixture(scope="module")
def chat_service(nlp_pipeline, catalog):
    return ChatbotService(pipeline=nlp_pipeline, catalog=catalog)


# =====================================================================
# 1. Testes do Pipeline de Intenções (Scikit-Learn)
# =====================================================================

def test_intent_saudacao(nlp_pipeline):
    intent, conf = nlp_pipeline.predict_intent("Olá, bom dia!")
    assert intent == "saudacao"
    assert conf > 0.40

def test_intent_disponibilidade_especifica(nlp_pipeline):
    frases = [
        "Tem arduino uno disponível?",
        "tem osciloscópio livre no lab?",
        "vocês têm cabo mini usb?",
        "tem placa perfurada sobrando?"
    ]
    for f in frases:
        intent, conf = nlp_pipeline.predict_intent(f)
        assert intent == "consultar_disponibilidade", f"Falhou para: {f} (previu {intent})"
        assert conf > 0.30

def test_intent_localizacao(nlp_pipeline):
    frases = [
        "Onde fica a estação de solda?",
        "onde estão os jumpers?",
        "em qual armário fica a ponte h?"
    ]
    for f in frases:
        intent, conf = nlp_pipeline.predict_intent(f)
        assert intent == "consultar_localizacao", f"Falhou para: {f} (previu {intent})"

def test_intent_regras_emprestimo(nlp_pipeline):
    frases = [
        "Como funciona o empréstimo?",
        "posso levar o multímetro pra casa?",
        "qual o prazo de devolução para fazer tcc?"
    ]
    for f in frases:
        intent, conf = nlp_pipeline.predict_intent(f)
        assert intent == "regras_emprestimo", f"Falhou para: {f} (previu {intent})"

def test_intent_horario(nlp_pipeline):
    frases = [
        "Qual o horário de funcionamento do laboratório?",
        "que horas o lab abre?",
        "até que horas posso devolver o material hoje?"
    ]
    for f in frases:
        intent, conf = nlp_pipeline.predict_intent(f)
        assert intent == "horario_funcionamento", f"Falhou para: {f} (previu {intent})"

def test_intent_despedida(nlp_pipeline):
    intent, conf = nlp_pipeline.predict_intent("Muito obrigado, valeu!")
    assert intent == "despedida"


# =====================================================================
# 2. Testes de Extração de Entidades e Fuzzy Matching (RapidFuzz)
# =====================================================================

def test_fuzzy_match_exato_e_aproximado(catalog):
    # Match exato
    single, multi, score = catalog.match_item("Tem Cabo Mini USB disponível?")
    assert single is not None
    assert single["nome"] == "Cabo Mini USB"
    assert score >= 80.0

    # Match com acentuação ausente e erro leve
    single, multi, score = catalog.match_item("Tem modulo rele sobrando?")
    assert single is not None
    assert single["nome"] == "Modulo relé 8"
    assert score >= 75.0

def test_desambiguacao_proativa_jumper(catalog):
    """RN-008: Busca genérica por 'jumper' deve retornar as 3 variações de jumpers."""
    single, multi, score = catalog.match_item("Tem jumper pra bancada?")
    assert single is None
    assert len(multi) >= 3
    nomes = [it["nome"] for it in multi]
    assert "jumper femea x femea" in nomes
    assert "jumper macho x macho" in nomes

def test_desambiguacao_proativa_arduino(catalog):
    """RN-008: Busca genérica por 'arduino' deve listar as variações."""
    single, multi, score = catalog.match_item("Tem arduino?")
    assert single is None
    assert len(multi) >= 2
    nomes = [it["nome"] for it in multi]
    assert "Arduino mega2560" in nomes or "Arduino uno" in nomes

def test_item_nao_cadastrado(catalog):
    """RN-010: Item inexistente não deve atingir 75%."""
    single, multi, score = catalog.match_item("Vocês têm ferro de passar roupa?")
    assert single is None
    assert len(multi) == 0


# =====================================================================
# 3. Testes do Orquestrador de Serviço (Regras RN-008 a RN-011)
# =====================================================================

def test_service_item_disponivel(chat_service):
    res = chat_service.process_message("Tem Cabo Mini USB disponível?")
    assert "Sim! Temos 5 unidades de 'Cabo Mini USB' disponíveis" in res["reply"]
    assert res["matched_item"]["id"] == 7

def test_service_desambiguacao_resposta(chat_service):
    """RN-008: Resposta formatada listando modelos e contagens."""
    res = chat_service.process_message("Tem jumper?")
    assert "opções de 'jumper' no acervo:" in res["reply"]
    assert "jumper femea x femea: 950 unidades disponíveis" in res["reply"]
    assert "Qual dessas opções você precisa?" in res["reply"]

def test_service_item_indisponivel(chat_service):
    """RN-010: Item em manutenção deve responder exatamente 'Item indisponível no momento.'"""
    res = chat_service.process_message("Tem placa de fenolite livre?")
    assert res["reply"] == "Item indisponível no momento."

def test_service_item_inexistente(chat_service):
    """RN-010: Item ausente deve responder exatamente 'Item não cadastrado no acervo.'"""
    res = chat_service.process_message("Tem ferro de solda de 100W?")
    assert res["reply"] == "Item não cadastrado no acervo."

def test_service_horario_e_regras(chat_service):
    """RN-011: Leitura parametrizada de horários e regras."""
    res_horario = chat_service.process_message("Qual o horário de funcionamento?")
    assert "08h às 18h" in res_horario["reply"]

    res_regras = chat_service.process_message("Posso levar o multímetro pra casa?")
    assert "Componentes e ferramentas de bancada" in res_regras["reply"]
    assert "7 dias" in res_regras["reply"]

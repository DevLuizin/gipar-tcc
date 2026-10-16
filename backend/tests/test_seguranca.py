import pytest
from fastapi import HTTPException

from seguranca import (
    criar_token_acesso,
    obter_hash_senha,
    obter_usuario_atual,
    verificar_senha,
)

def test_verificar_senha_deve_retornar_true_para_senha_correta():
    senha_plana = "admin123"
    hash_correto = obter_hash_senha(senha_plana)

    assert verificar_senha(senha_plana, hash_correto) is True


def test_verificar_senha_deve_retornar_false_para_senha_incorreta():
    hash_correto = obter_hash_senha("admin123")

    assert verificar_senha("senha-incorreta", hash_correto) is False


class CursorFalso:
    def __init__(self, usuario):
        self.usuario = usuario

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, *_):
        return None

    def fetchone(self):
        return self.usuario


class ConexaoFalsa:
    def __init__(self, usuario):
        self.usuario = usuario

    def cursor(self):
        return CursorFalso(self.usuario)

    def close(self):
        return None


def test_token_version_atual_deve_autenticar(monkeypatch):
    usuario = {
        "id": 7,
        "email": "usuario@gipar.com",
        "tipo_usuario": "COMUM",
        "token_version": 3,
    }
    monkeypatch.setattr(
        "seguranca.pymysql.connect",
        lambda **_: ConexaoFalsa(usuario),
    )
    token = criar_token_acesso(
        {
            "sub": usuario["email"],
            "id": usuario["id"],
            "perfil": usuario["tipo_usuario"],
            "token_version": 3,
        }
    )

    autenticado = obter_usuario_atual(token)

    assert autenticado["id"] == usuario["id"]


def test_token_version_antiga_deve_ser_rejeitada(monkeypatch):
    usuario = {
        "id": 7,
        "email": "usuario@gipar.com",
        "tipo_usuario": "COMUM",
        "token_version": 4,
    }
    monkeypatch.setattr(
        "seguranca.pymysql.connect",
        lambda **_: ConexaoFalsa(usuario),
    )
    token = criar_token_acesso(
        {
            "sub": usuario["email"],
            "id": usuario["id"],
            "perfil": usuario["tipo_usuario"],
            "token_version": 3,
        }
    )

    with pytest.raises(HTTPException) as erro:
        obter_usuario_atual(token)

    assert erro.value.status_code == 401
    

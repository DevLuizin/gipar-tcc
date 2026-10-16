"""Validação dos contratos de perfil definidos no REQ-003."""

import pytest
from pydantic import ValidationError

from models.models import AlterarSenhaRequest, AtualizarPerfilRequest


def test_atualizar_perfil_normaliza_email():
    dados = AtualizarPerfilRequest(
        nome="Usuário Teste",
        email=" USUARIO@EXEMPLO.COM ",
        avatar="robo-azul",
    )

    assert dados.email == "usuario@exemplo.com"


@pytest.mark.parametrize(
    "nova_senha",
    ["curta1", "abcdefgh", "12345678"],
)
def test_nova_senha_deve_seguir_politica(nova_senha):
    with pytest.raises(ValidationError):
        AlterarSenhaRequest(
            senha_atual="senhaAtual1",
            nova_senha=nova_senha,
            confirmacao_senha=nova_senha,
        )


def test_confirmacao_de_senha_deve_ser_identica():
    with pytest.raises(ValidationError):
        AlterarSenhaRequest(
            senha_atual="senhaAtual1",
            nova_senha="novaSenha1",
            confirmacao_senha="outraSenha1",
        )

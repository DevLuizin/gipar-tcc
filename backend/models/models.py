from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

class TipoUsuario(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    TECNICO = "TECNICO"
    COMUM = "COMUM"


class TemaUsuario(str, Enum):
    INSTITUCIONAL = "institucional"
    DARK = "dark"
    OCEAN = "ocean"
    ALTO_CONTRASTE = "alto-contraste"


class AvatarUsuario(str, Enum):
    ROBO_AZUL = "robo-azul"
    ROBO_VERDE = "robo-verde"
    ROBO_ROXO = "robo-roxo"
    CIRCUITO_AZUL = "circuito-azul"
    CIRCUITO_VERDE = "circuito-verde"
    CIRCUITO_LARANJA = "circuito-laranja"

class StatusEquipamento(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    EM_USO = "EM_USO"
    RESERVADO = "RESERVADO"
    EM_MANUTENCAO = "EM_MANUTENCAO"
    INATIVO = "INATIVO"

class StatusManutencao(str, Enum):
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

class StatusReserva(str, Enum):
    PENDENTE = "PENDENTE"
    EFETIVADA = "EFETIVADA"
    CANCELADA = "CANCELADA"

class StatusEmprestimo(str, Enum):
    ATIVO = "ATIVO"
    DEVOLVIDO = "DEVOLVIDO"
    ATRASADO = "ATRASADO"
    CANCELADO = "CANCELADO"


# ================================================================
# MODELOS
# ================================================================

class EmprestimoUpdate(BaseModel):
    data_previsao_devolucao: Optional[datetime] = None
    observacoes: Optional[str] = None
    status: Optional[StatusEmprestimo] = None
    id_tecnico_retorno: Optional[int] = None

class ManutencaoUpdate(BaseModel):
    id_equipamento: Optional[int] = None
    tipo: Optional[str] = None 
    descricao_defeito: Optional[str] = None
    status: Optional[StatusManutencao] = None
    data_conclusao: Optional[datetime] = None

class Categoria(BaseModel):
    nome: str
    descricao: Optional[str] = None


class Usuario(BaseModel):
    nome: str
    email: str
    senha: str
    tipo_usuario: TipoUsuario = TipoUsuario.COMUM
    ativo: Optional[bool] = True


class PerfilUsuarioResponse(BaseModel):
    id: int
    nome: str
    nome_exibicao: Optional[str] = None
    email: str
    tipo_usuario: TipoUsuario
    avatar: Optional[AvatarUsuario] = None
    tema: TemaUsuario = TemaUsuario.INSTITUCIONAL
    data_cadastro: Optional[datetime] = None


class AtualizarPerfilRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    nome_exibicao: Optional[str] = Field(default=None, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    avatar: Optional[AvatarUsuario] = None
    senha_atual: Optional[str] = None

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()
        if len(valor) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres")
        return valor

    @field_validator("nome_exibicao")
    @classmethod
    def normalizar_nome_exibicao(cls, valor):
        if valor is None:
            return None
        return valor.strip() or None

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if "@" not in valor or valor.startswith("@") or valor.endswith("@"):
            raise ValueError("E-mail inválido")
        return valor


class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=8)
    confirmacao_senha: str

    @field_validator("nova_senha")
    @classmethod
    def validar_forca_senha(cls, valor: str) -> str:
        if not any(caractere.isalpha() for caractere in valor):
            raise ValueError("A nova senha deve conter pelo menos uma letra")
        if not any(caractere.isdigit() for caractere in valor):
            raise ValueError("A nova senha deve conter pelo menos um número")
        return valor

    @model_validator(mode="after")
    def validar_confirmacao(self):
        if self.nova_senha != self.confirmacao_senha:
            raise ValueError("A confirmação da senha não confere")
        if self.nova_senha == self.senha_atual:
            raise ValueError("A nova senha deve ser diferente da senha atual")
        return self


class AtualizarTemaRequest(BaseModel):
    tema: TemaUsuario


class Equipamento(BaseModel):
    codigo_patrimonio: str
    nome: str
    modelo: Optional[str] = None
    id_categoria: int
    quantidade: int = Field(default=1, ge=1)
    status: StatusEquipamento = StatusEquipamento.DISPONIVEL
    ativo: Optional[bool] = True


class Manutencao(BaseModel):
    id: Optional[int] = None
    id_equipamento: int
    tipo: str 
    descricao_defeito: str
    data_abertura: Optional[str] = None
    status: StatusManutencao = StatusManutencao.PENDENTE
    data_conclusao: Optional[datetime] = None

class Reserva(BaseModel):
    id_equipamento: int
    id_usuario: int
    data_reserva: date
    status: StatusReserva = StatusReserva.PENDENTE


class Emprestimo(BaseModel):
    id_usuario: int
    id_equipamento: int
    id_tecnico_saida: int
    id_tecnico_retorno: Optional[int] = None
    data_retirada: Optional[datetime] = None
    data_previsao_devolucao: datetime
    data_devolucao_real: Optional[datetime] = None
    observacoes: Optional[str] = None
    status: StatusEmprestimo = StatusEmprestimo.ATIVO

class LogAuditoria(BaseModel):
    id: Optional[int] = None
    id_usuario: Optional[int] = None
    acao: str
    tabela_afetada: str
    id_registro_afetado: Optional[int] = None
    detalhes: Optional[str] = None
    data_acao: Optional[datetime] = None

    class Config:
        from_attributes = True

class HistoricoMovimentacao(BaseModel):
    id: Optional[int] = None
    id_equipamento: int
    id_usuario_acao: int
    status_anterior: Optional[StatusEquipamento] = None
    status_novo: Optional[StatusEquipamento] = None
    descricao_motivo: str
    data_movimentacao: Optional[datetime] = None

    class Config:
        from_attributes = True

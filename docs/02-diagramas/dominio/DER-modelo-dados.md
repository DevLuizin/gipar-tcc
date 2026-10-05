# Diagrama Entidade-Relacionamento (DER) — Modelo de Domínio GIPAR

Este documento formaliza o modelo relacional de banco de dados do GIPAR, mapeando as entidades, atributos, chaves primárias/estrangeiras e cardinalidades do MySQL.

---

## 1. Diagrama Entidade-Relacionamento (Mermaid)

```mermaid
erDiagram
    categoria ||--o{ equipamento : "classifica"
    equipamento ||--o{ manutencao : "sofre"
    equipamento ||--o{ reserva : "recebe"
    equipamento ||--o{ emprestimo : "pertence"
    equipamento ||--o{ historico_movimentacao : "possui"

    usuario ||--o{ reserva : "solicita"
    usuario ||--o{ emprestimo : "retira"
    usuario ||--o{ emprestimo : "libera (tecnico_saida)"
    usuario ||--o{ emprestimo : "recebe (tecnico_retorno)"
    usuario ||--o{ historico_movimentacao : "executa"
    usuario ||--o{ logs_auditoria : "gera"

    categoria {
        int id PK
        string nome UK
        text descricao
        timestamp data_criacao
    }

    usuario {
        int id PK
        string nome
        string email UK
        string senha
        enum tipo_usuario
        boolean ativo
        timestamp data_cadastro
    }

    equipamento {
        int id PK
        string codigo_patrimonio UK
        string nome
        string modelo
        int id_categoria FK
        int quantidade
        string status
        boolean ativo
    }

    manutencao {
        int id PK
        int id_equipamento FK
        text descricao_defeito
        enum tipo
        string status
        boolean ativo
        datetime data_abertura
        datetime data_conclusao
    }

    reserva {
        int id PK
        int id_equipamento FK
        int id_usuario FK
        date data_reserva
        string status
        timestamp data_solicitacao
    }

    emprestimo {
        int id PK
        int id_equipamento FK
        int id_usuario FK
        int id_tecnico_saida FK
        int id_tecnico_retorno FK
        datetime data_retirada
        datetime data_previsao_devolucao
        datetime data_devolucao_real
        text observacoes
        enum status
    }

    historico_movimentacao {
        int id PK
        int id_equipamento FK
        int id_usuario_acao FK
        string status_anterior
        string status_novo
        string descricao_motivo
        timestamp data_movimentacao
    }

    logs_auditoria {
        int id PK
        int id_usuario FK
        string acao
        string tabela_afetada
        int id_registro_afetado
        text detalhes
        timestamp data_acao
    }
```

---

## 2. Descrição das Entidades e Regras de Integridade

| Tabela | Responsabilidade de Negócio | Regra de Chave e Integridade |
| :--- | :--- | :--- |
| `categoria` | Agrupamento de itens (ex: Instrumentação, Componentes, Robótica). | `nome` é único (`UNIQUE`). |
| `usuario` | Cadastro de operadores e solicitantes com papéis de acesso. | `email` único, senha com hash. |
| `equipamento` | Cadastro físico do item/equipamento do laboratório. | `codigo_patrimonio` único; `id_categoria` obrigatório. |
| `manutencao` | Acompanhamento de defeitos, consertos e calibrações. | Vinculado a `equipamento`. |
| `reserva` | Agendamento prévio de item para data futura. | Validação de datas sem sobreposição. |
| `emprestimo` | Registro de saída, custódia e retorno físico de itens. | Registra técnico de entrega e recebimento. |
| `historico_movimentacao` | Trilha de auditoria das transições de status do item. | Chaves para `equipamento` e `usuario`. |
| `logs_auditoria` | Log de operações e auditoria de ações no sistema. | Rastreabilidade administrativa. |

## 3. Rastreabilidade
- **Arquivo-fonte DDL:** [`docker/mysql/init.sql`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/docker/mysql/init.sql)
- **Regras de Negócio:** `RN-001`, `RN-002`, `RN-003`, `RN-004`, `RN-005`
- **Requisitos:** `REQ-001`, `REQ-004`

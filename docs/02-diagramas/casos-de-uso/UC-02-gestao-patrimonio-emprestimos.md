# Diagrama de Casos de Uso — UC-02: Gestão de Patrimônio e Empréstimos

Este documento mapeia os casos de uso centrais do GIPAR herdados da baseline e revisados para a evolução do sistema.

---

## 1. Visão Geral

Representa as funções administrativas, de controle patrimonial e operacionais exercidas por Técnicos, Administradores e Solicitantes.

## 2. Diagrama de Casos de Uso (Mermaid)

```mermaid
flowchart LR
    subgraph Atores["Atores"]
        Admin["Administrador"]
        Tecnico["Técnico / Laboratorista"]
        Solicitante["Solicitante (Professor/Aluno)"]
    end

    subgraph ModuloPatrimonio["Módulo de Patrimônio e Laboratório"]
        UC21["UC-02.1: Cadastrar / Editar Item de Laboratório"]
        UC22["UC-02.2: Consultar e Filtrar Acervo"]
        UC23["UC-02.3: Registrar Baixa / Manutenção de Item"]
        UC24["UC-02.4: Importar Dados de Planilha SQL"]
    end

    subgraph ModuloEmprestimos["Módulo de Empréstimos e Reservas"]
        UC31["UC-02.5: Solicitar Reserva de Equipamento"]
        UC32["UC-02.6: Registrar Retirada (Empréstimo Ativo)"]
        UC33["UC-02.7: Registrar Devolução e Vistoria"]
        UC34["UC-02.8: Consultar Histórico e Pendências"]
    end

    subgraph ModuloUsuarios["Módulo de Acessos e Configurações"]
        UC41["UC-02.9: Gerenciar Usuários e Permissões"]
        UC42["UC-02.10: Atualizar Perfil e Senha"]
        UC43["UC-02.11: Configurar Tema Visual"]
    end

    Solicitante --> UC22
    Solicitante --> UC31
    Solicitante --> UC34
    Solicitante --> UC42
    Solicitante --> UC43

    Tecnico --> UC21
    Tecnico --> UC22
    Tecnico --> UC23
    Tecnico --> UC32
    Tecnico --> UC33
    Tecnico --> UC34
    Tecnico --> UC42
    Tecnico --> UC43

    Admin --> UC21
    Admin --> UC23
    Admin --> UC24
    Admin --> UC32
    Admin --> UC33
    Admin --> UC41
    Admin --> UC42
```

## 3. Rastreabilidade
- **Requisitos:** [[docs/01-requisitos/requisitos/REQ-002-responsividade-mobile|REQ-002]], [[docs/01-requisitos/requisitos/REQ-003-gestao-usuarios-temas|REQ-003]], [[docs/01-requisitos/requisitos/REQ-004-filtros-pesquisa-listagens|REQ-004]]
- **Regras de Negócio:** `RN-001` a `RN-007`

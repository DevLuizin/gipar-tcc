-- =====================================================================
-- SCRIPT DE INICIALIZAÇÃO DO BANCO DE DADOS - PROJETO GIPAR
-- Consolidado para Docker
-- =====================================================================

CREATE DATABASE IF NOT EXISTS gipar_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE gipar_db;

-- 1. TABELA: categoria
CREATE TABLE IF NOT EXISTS categoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. TABELA: usuario
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo_usuario ENUM('ADMINISTRADOR', 'TECNICO', 'COMUM') DEFAULT 'COMUM',
    ativo BOOLEAN DEFAULT TRUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. TABELA: equipamento
CREATE TABLE IF NOT EXISTS equipamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_patrimonio VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    modelo VARCHAR(100),
    id_categoria INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    status VARCHAR(30) DEFAULT 'DISPONIVEL',
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 4. TABELA: manutencao
CREATE TABLE IF NOT EXISTS manutencao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_equipamento INT NOT NULL,
    descricao_defeito TEXT NOT NULL,
    tipo ENUM('PREVENTIVA', 'CORRETIVA') DEFAULT 'CORRETIVA',
    status VARCHAR(30) DEFAULT 'PENDENTE',
    ativo BOOLEAN DEFAULT TRUE,
    data_abertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_conclusao DATETIME NULL,
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 5. TABELA: reserva
CREATE TABLE IF NOT EXISTS reserva (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_equipamento INT NOT NULL,
    id_usuario INT NOT NULL,
    data_reserva DATE NOT NULL,
    status VARCHAR(30) DEFAULT 'PENDENTE',
    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 6. TABELA: emprestimo
CREATE TABLE IF NOT EXISTS emprestimo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_equipamento INT NOT NULL,
    id_usuario INT NOT NULL,
    id_tecnico_saida INT NOT NULL,
    id_tecnico_retorno INT NULL,
    data_retirada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_previsao_devolucao DATETIME NOT NULL,
    data_devolucao_real DATETIME NULL,
    observacoes TEXT,
    status ENUM('ATIVO', 'DEVOLVIDO', 'ATRASADO', 'CANCELADO') NOT NULL DEFAULT 'ATIVO',
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_tecnico_saida) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_tecnico_retorno) REFERENCES usuario(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 7. TABELA: historico_movimentacao
CREATE TABLE IF NOT EXISTS historico_movimentacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_equipamento INT NOT NULL,
    id_usuario_acao INT NOT NULL,
    status_anterior VARCHAR(255),
    status_novo VARCHAR(255),
    descricao_motivo VARCHAR(255) NOT NULL,
    data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario_acao) REFERENCES usuario(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 8. TABELA: logs_auditoria
CREATE TABLE IF NOT EXISTS logs_auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL,
    acao VARCHAR(50) NOT NULL,
    tabela_afetada VARCHAR(50) NOT NULL,
    id_registro_afetado INT NULL,
    detalhes TEXT,
    data_acao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE SET NULL
) ENGINE=InnoDB;

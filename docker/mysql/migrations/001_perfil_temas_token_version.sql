-- REQ-003 / ADR-006
-- Executar uma única vez em bancos GIPAR já existentes.

ALTER TABLE usuario
    ADD COLUMN nome_exibicao VARCHAR(100) NULL AFTER nome;

ALTER TABLE usuario
    ADD COLUMN avatar VARCHAR(50) NULL AFTER ativo;

ALTER TABLE usuario
    ADD COLUMN tema VARCHAR(30) NOT NULL DEFAULT 'institucional' AFTER avatar;

ALTER TABLE usuario
    ADD COLUMN token_version INT NOT NULL DEFAULT 0 AFTER tema;

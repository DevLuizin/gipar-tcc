#!/usr/bin/env python3
"""Importador de planilha de equipamentos para o banco MySQL.

Uso:
  python import_equipamentos.py path/to/planilha.csv

Suporta CSV e XLSX (se `pandas` estiver instalado).
O script usa as variáveis de ambiente definidas em `backend/.env`.
"""
from pathlib import Path
import os
import argparse
import csv
import logging
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

LOG_FILE_PATH = Path(__file__).resolve().parent / "import_equipamentos.log"

try:
    import pandas as pd
    _HAS_PANDAS = True
except Exception:
    _HAS_PANDAS = False

CATEGORY_KEYWORDS = {
    # Ferramentas e Instrumentos de Bancada
    "Equipamentos de Medição": ["osciloscopio", "osciloscópio", "multimetro", "multímetro", "amperimetro", "voltímetro", "voltimetro", "gerador de função", "analisador"],
    "Ferramentas e Soldagem": ["ferro de solda", "estacao de solda", "estação de solda", "sugador", "estanho", "alicate", "chave de fenda", "chave philips", "pinça", "protoboard", "matriz de contatos"],
    
    # Placas e Microcontroladores
    "Microcontroladores e Placas": ["arduino", "esp32", "esp8266", "nodemcu", "raspberry", "mega2560", "mega", "uno", "nano", "digispark", "pic", "stm32"],
    
    # Sensores e Módulos de Entrada
    "Sensores e Transdutores": ["sensor", "ultrassonico", "ultrassônico", "ldr", "capacitivo", "indutivo", "pir", "presença", "umidade", "temperatura", "lm35", "dht11", "dht22", "encoder", "giroscópio", "giroscopio", "acelerometro", "corrente", "tensao", "tensão", "zmct103c", "peso", "celula de carga", "hx711", "ponte de wheatstone"],
    "Módulos de Comunicação": ["bluetooth", "hc-05", "hc-06", "wifi", "rfid", "nfc", "rf", "radio", "lora", "gps", "ethernet"],
    
    # Atuadores e Saídas
    "Motores e Drivers": ["servo", "stepper", "motor", "passo", "dc", "driver", "l298n", "a4988", "ponte h"],
    "Displays e Sinalização": ["display", "oled", "lcd", "matriz", "led", "rgb", "buzzer", "sirene"],
    "Chaveamento e Controle": ["relé", "rele", "transistor", "mosfet", "tip120", "tip122", "bc547", "bc548"],
    
    # Componentes Eletrônicos Passivos e Ativos
    "Componentes Discretos": ["resistor", "potenciometro", "potenciômetro", "trimpot", "capacitor", "diodo", "indutor", "cristal", "oscilador"],
    "Circuitos Integrados (CIs)": ["ci", "circuito integrado", "555", "lm317", "lm7805", "lm7812", "opamp", "amplificador operacional", "ad620", "amplificador de transimpedancia"],
    
    # Conectividade e Estrutura
    "Cabos e Conexões": ["cabo", "jumper", "fio", "conector", "plug", "terminal", "barra de pinos", "jacare", "garra", "usb", "p4", "bnc"],
    "Fontes e Energia": ["fonte", "bateria", "pilha", "carregador", "step-up", "step-down", "boost", "buck", "dc-dc", "bms", "painel solar", "placa solar", "microinversor"],
    
    # Agrupamentos
    "Kits Didáticos": ["kit"]
}


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower().replace("ç", "c").replace("ã", "a").replace("õ", "o").replace("á", "a").replace("â", "a").replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o").replace("ô", "o").replace("ú", "u").replace("à", "a").replace("ü", "u")


def infer_category_from_name(nome):
    nome_tratado = normalize_text(nome)
    for categoria, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in nome_tratado:
                return categoria
    return None


def setup_logging():
    logger = logging.getLogger("import_equipamentos")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger



def load_db_config():
    # Procura o .env dentro da pasta backend ou no ambiente atual
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    config = {
        "host": os.getenv("host") or os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("user") or os.getenv("DB_USER", "root"),
        "password": os.getenv("password") if os.getenv("password") is not None else os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("database") or os.getenv("DB_NAME", "gipar_db"),
        "cursorclass": DictCursor,
    }
    return config


def normalize_key(key: str):
    if key is None:
        return ""
    text = key.strip().lower()
    text = text.replace(" ", "_")
    text = text.replace("ç", "c").replace("ã", "a").replace("õ", "o").replace("á", "a").replace("â", "a")
    text = text.replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o").replace("ô", "o")
    text = text.replace("ú", "u").replace("à", "a").replace("ü", "u")
    return text


def sanitize_text(value, max_length=None):
    if value is None:
        return ""
    text = str(value).strip()
    if max_length is not None and len(text) > max_length:
        return text[:max_length]
    return text


def normalize_row(row: dict):
    # Normaliza nomes de colunas comuns
    lower = {normalize_key(k): sanitize_text(v) for k, v in row.items()}

    def pick(*names, default=None):
        for n in names:
            if n in lower and lower[n] not in (None, ""):
                return lower[n]
        return default

    codigo = pick("codigo_patrimonio", "codigo", "patrimonio", "codigo")
    nome = pick(
        "nome", "descricao", "descricao_equipamento", "material_de_consumo",
        "material", "item"
    )
    modelo = pick("modelo", "modelo_equipamento", None)
    categoria = pick("categoria", "categoria_nome", "nome_categoria", "tipo", None)
    categoria_id = pick("id_categoria", "categoria_id", None)
    quantidade = pick(
        "quantidade", "qtd", "quantidade_equipamento", "quantidade_disponivel",
        "quantidade_disponivel", 1
    )

    try:
        quantidade = int(float(str(quantidade).strip().replace("~", "")))
        if quantidade < 1:
            quantidade = 1
    except Exception:
        quantidade = 1

    return {
        "codigo_patrimonio": sanitize_text(codigo, max_length=50),
        "nome": sanitize_text(nome, max_length=100),
        "modelo": sanitize_text(modelo, max_length=100),
        "categoria": sanitize_text(categoria, max_length=50),
        "categoria_id": sanitize_text(categoria_id),
        "quantidade": quantidade,
    }


def read_sheet(path: Path):
    ext = path.suffix.lower()
    rows = []

    if ext in (".xls", ".xlsx"):
        if not _HAS_PANDAS:
            raise RuntimeError("Leitura de XLSX requer 'pandas' e 'openpyxl'. Instale-os e tente novamente.")
        df = pd.read_excel(path)
        df = df.fillna("")
        for _, r in df.iterrows():
            rows.append({str(k): v for k, v in r.items()})

    elif ext == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)

    else:
        raise RuntimeError("Formato de arquivo não suportado. Use .csv ou .xlsx")

    return rows


def get_or_create_category(config, categoria_nome, logger):
    if not categoria_nome:
        categoria_nome = "Sem Categoria"

    con = None
    cur = None
    try:
        con = pymysql.connect(**config)
        cur = con.cursor()
        cur.execute("SELECT id FROM categoria WHERE nome = %s", (categoria_nome,))
        categoria = cur.fetchone()
        if categoria:
            return categoria["id"] if isinstance(categoria, dict) else categoria[0]

        cur.execute(
            "INSERT INTO categoria (nome, descricao) VALUES (%s, %s)",
            (categoria_nome, "Categoria automática criada a partir da importação")
        )
        con.commit()
        categoria_id = cur.lastrowid
        logger.info("Categoria criada automaticamente: %s (%d)", categoria_nome, categoria_id)
        return categoria_id
    except Exception:
        if con:
            con.rollback()
        logger.exception("Erro ao criar ou buscar categoria %s", categoria_nome)
        raise
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def resolve_category_id(config, categoria, categoria_id, default_category, logger):
    if categoria_id:
        try:
            return int(str(categoria_id).strip())
        except Exception:
            pass

    if not categoria:
        categoria = default_category

    categoria = sanitize_text(categoria, max_length=50)
    return get_or_create_category(config, categoria or default_category, logger)


def insert_rows(config, normalized_rows, logger, default_category):
    sql = (
        "INSERT INTO equipamento (codigo_patrimonio, nome, modelo, id_categoria, quantidade) "
        "VALUES (%s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE nome = VALUES(nome), modelo = VALUES(modelo), "
        "id_categoria = VALUES(id_categoria), quantidade = VALUES(quantidade)"
    )
    con = None
    cur = None
    inserted = 0
    updated = 0
    skipped = 0
    try:
        con = pymysql.connect(**config)
        cur = con.cursor()
        for r in normalized_rows:
            if not r["codigo_patrimonio"] or not r["nome"]:
                skipped += 1
                logger.warning("Linha ignorada por falta de codigo_patrimonio ou nome: %s", r)
                continue

            category_id = resolve_category_id(config, r.get("categoria"), r.get("categoria_id"), default_category, logger)
            cur.execute(sql, (r["codigo_patrimonio"], r["nome"], r["modelo"], category_id, r["quantidade"]))
            if cur.rowcount == 1:
                inserted += 1
                logger.info("Inserido equipamento %s com categoria %s (%s)", r["codigo_patrimonio"], r.get("categoria"), category_id)
            elif cur.rowcount == 2:
                updated += 1
                logger.info("Atualizado equipamento %s com categoria %s (%s)", r["codigo_patrimonio"], r.get("categoria"), category_id)
            else:
                inserted += 1
        con.commit()
    except Exception:
        if con:
            con.rollback()
        logger.exception("Erro ao inserir linhas no banco")
        raise
    finally:
        if cur:
            cur.close()
        if con:
            con.close()

    return inserted, updated, skipped


def main():
    parser = argparse.ArgumentParser(description="Importa equipamentos de planilha para o banco MySQL")
    parser.add_argument("file", help="Caminho para .csv ou .xlsx com os equipamentos")
    parser.add_argument("--default-category", default="Sem Categoria", help="Categoria padrão quando não for encontrada outra categoria")
    parser.add_argument("--infer-category", action="store_true", help="Tenta inferir categoria a partir do nome do equipamento")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print("Arquivo não encontrado:", path)
        return

    try:
        rows = read_sheet(path)
    except Exception as e:
        print("Erro ao ler planilha:", e)
        return

    logger = setup_logging()
    logger.info("Iniciando importação de %s", path)
    logger.info("Arquivo de log: %s", LOG_FILE_PATH)

    normalized = [normalize_row(r) for r in rows]
    if args.infer_category:
        for item in normalized:
            if not item.get("categoria") and item.get("nome"):
                item["categoria"] = infer_category_from_name(item["nome"]) or args.default_category

    logger.info("Linhas lidas: %d", len(rows))

    config = load_db_config()

    try:
        inserted, updated, skipped = insert_rows(config, normalized, logger, args.default_category)
        logger.info("Importação concluída. %d itens inseridos, %d atualizados, %d ignorados.", inserted, updated, skipped)
    except Exception as e:
        logger.error("Erro ao inserir no banco: %s", e)


if __name__ == "__main__":
    main()

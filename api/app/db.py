"""Acesso ao SQLite. Todas as consultas usam parâmetros (nunca concatenação de strings)."""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS relatos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo          TEXT    NOT NULL,
    descricao     TEXT    NOT NULL DEFAULT '',
    lat           REAL    NOT NULL,
    lon           REAL    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'novo',
    prioridade    TEXT,
    protocolo     TEXT,
    origem        TEXT    NOT NULL DEFAULT 'app',
    confirmacoes  INTEGER NOT NULL DEFAULT 0,
    simulado      INTEGER NOT NULL DEFAULT 0,
    criado_em     TEXT    NOT NULL,
    atualizado_em TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_relatos_status ON relatos(status);

CREATE TABLE IF NOT EXISTS historico (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    relato_id  INTEGER NOT NULL REFERENCES relatos(id),
    status     TEXT    NOT NULL,
    nota       TEXT,
    autor      TEXT    NOT NULL,
    em         TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_historico_relato ON historico(relato_id);
"""


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def caminho_db() -> str:
    return os.environ.get("DB_PATH", "/data/passolivre.db")


@contextmanager
def conexao():
    con = sqlite3.connect(caminho_db(), timeout=5)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def inicializar() -> None:
    with conexao() as con:
        con.execute("PRAGMA journal_mode = WAL")
        con.executescript(SCHEMA)

"""Passo Livre — API do MVP.

Mapa colaborativo de obstáculos em calçadas e pontos de ônibus de São Paulo.
Contratos documentados em docs/contratos.md e em /api/docs (OpenAPI).

Princípios: nenhum dado pessoal é coletado ou registrado (LGPD), SQL sempre parametrizado,
tokens comparados em tempo constante, rate limit sem guardar IP.
"""

import hashlib
import logging
import os
import secrets
import sys
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field, field_validator

from . import db, seed

# ---------------------------------------------------------------- configuração

APP_VERSION = os.environ.get("APP_VERSION", "local")
RPA_TOKEN = os.environ.get("RPA_TOKEN", "")
ROBO_TOKEN = os.environ.get("ROBO_TOKEN", "")
SEED_DEMO = os.environ.get("SEED_DEMO", "true").lower() == "true"
LIMITE_POR_MINUTO = int(os.environ.get("RATE_LIMIT_POR_MINUTO", "10"))

# Retângulo aproximado do município de São Paulo
SP_LAT = (-24.01, -23.35)
SP_LON = (-46.83, -46.36)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='{"ts":"%(asctime)s","nivel":"%(levelname)s","msg":"%(message)s"}',
)
log = logging.getLogger("passolivre")


class Tipo(str, Enum):
    buraco = "buraco"
    carro_na_calcada = "carro_na_calcada"
    entulho = "entulho"
    degrau_sem_rampa = "degrau_sem_rampa"
    ponto_onibus_inacessivel = "ponto_onibus_inacessivel"
    calcada_estreita = "calcada_estreita"
    arvore_raiz = "arvore_raiz"
    iluminacao = "iluminacao"
    outro = "outro"


ROTULOS_TIPO = {
    "buraco": "Buraco ou piso quebrado",
    "carro_na_calcada": "Carro ou moto na calçada",
    "entulho": "Entulho ou lixo bloqueando",
    "degrau_sem_rampa": "Degrau sem rampa",
    "ponto_onibus_inacessivel": "Ponto de ônibus inacessível",
    "calcada_estreita": "Calçada estreita ou obstruída",
    "arvore_raiz": "Raiz de árvore levantando o piso",
    "iluminacao": "Falta de iluminação",
    "outro": "Outro obstáculo",
}


class Status(str, Enum):
    novo = "novo"
    em_analise = "em_analise"
    encaminhado = "encaminhado"
    resolvido = "resolvido"
    duplicado = "duplicado"


class Prioridade(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"


class Origem(str, Enum):
    app = "app"
    robo = "robo"


# ---------------------------------------------------------------- modelos


class RelatoEntrada(BaseModel):
    tipo: Tipo
    descricao: str = Field(default="", max_length=280)
    lat: float = Field(ge=SP_LAT[0], le=SP_LAT[1], description="Latitude dentro do município de SP")
    lon: float = Field(ge=SP_LON[0], le=SP_LON[1], description="Longitude dentro do município de SP")
    origem: Origem = Origem.app

    @field_validator("descricao")
    @classmethod
    def limpar(cls, v: str) -> str:
        return " ".join(v.split())


class AtualizacaoStatus(BaseModel):
    status: Status
    prioridade: Optional[Prioridade] = None
    protocolo: Optional[str] = Field(default=None, max_length=40, pattern=r"^[A-Za-z0-9\-_/]+$")
    nota: Optional[str] = Field(default=None, max_length=280)


class Relato(BaseModel):
    id: int
    tipo: str
    tipo_rotulo: str
    descricao: str
    lat: float
    lon: float
    status: str
    prioridade: Optional[str]
    protocolo: Optional[str]
    origem: str
    confirmacoes: int
    simulado: bool
    criado_em: str
    atualizado_em: str


class EventoHistorico(BaseModel):
    status: str
    nota: Optional[str]
    autor: str
    em: str


class RelatoDetalhe(Relato):
    historico: list[EventoHistorico]


def para_relato(row) -> dict:
    d = dict(row)
    d["simulado"] = bool(d["simulado"])
    d["tipo_rotulo"] = ROTULOS_TIPO.get(d["tipo"], d["tipo"])
    return d


# ---------------------------------------------------------------- segurança


class LimitadorDeTaxa:
    """Janela deslizante em memória. A chave é um hash diário do IP: o IP nunca é guardado."""

    def __init__(self, limite: int, janela_s: int = 60):
        self.limite = limite
        self.janela = janela_s
        self.eventos: dict[str, deque] = defaultdict(deque)
        self.sal = secrets.token_hex(16)

    def chave(self, request: Request) -> str:
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not ip and request.client:
            ip = request.client.host
        dia = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return hashlib.sha256(f"{self.sal}|{dia}|{ip}".encode()).hexdigest()[:20]

    def verificar(self, request: Request) -> None:
        agora = time.monotonic()
        fila = self.eventos[self.chave(request)]
        while fila and agora - fila[0] > self.janela:
            fila.popleft()
        if len(fila) >= self.limite:
            raise HTTPException(status_code=429, detail="Muitas requisições. Tente de novo em instantes.")
        fila.append(agora)
        if len(self.eventos) > 50_000:  # evita crescimento sem limite
            self.eventos.clear()


limitador = LimitadorDeTaxa(LIMITE_POR_MINUTO)


def token_valido(recebido: str, esperado: str) -> bool:
    return bool(esperado) and secrets.compare_digest(recebido.encode(), esperado.encode())


def exigir_token_rpa(authorization: str = Header(default="")) -> str:
    recebido = authorization.removeprefix("Bearer ").strip()
    if not token_valido(recebido, RPA_TOKEN):
        raise HTTPException(status_code=401, detail="Token do RPA inválido ou ausente.")
    return "rpa"


# ---------------------------------------------------------------- app


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    db.inicializar()
    if SEED_DEMO:
        inseridos = seed.popular_se_vazio()
        if inseridos:
            log.info("seed: %s relatos simulados inseridos", inseridos)
    log.info("api iniciada versao=%s", APP_VERSION)
    yield


app = FastAPI(
    title="Passo Livre API",
    version=APP_VERSION,
    description="Mapa colaborativo de obstáculos em calçadas e pontos de ônibus de São Paulo.",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    lifespan=ciclo_de_vida,
)

Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics", "/healthz"],
).instrument(app, metric_namespace="passolivre").expose(app, endpoint="/metrics", include_in_schema=False)


@app.middleware("http")
async def registrar(request: Request, call_next):
    """Log de acesso sem IP, sem user-agent e sem corpo (LGPD)."""
    inicio = time.perf_counter()
    resposta = await call_next(request)
    if request.url.path not in ("/metrics", "/healthz"):
        ms = (time.perf_counter() - inicio) * 1000
        log.info("%s %s %s %.1fms", request.method, request.url.path, resposta.status_code, ms)
    return resposta


# ---------------------------------------------------------------- rotas operacionais


@app.get("/healthz", include_in_schema=False)
def healthz():
    with db.conexao() as con:
        con.execute("SELECT 1").fetchone()
    return {"status": "ok"}


@app.get("/version", include_in_schema=False)
def version():
    return {"versao": APP_VERSION}


# ---------------------------------------------------------------- rotas do produto


@app.get("/api/tipos", tags=["referência"])
def listar_tipos():
    return [{"id": k, "rotulo": v} for k, v in ROTULOS_TIPO.items()]


@app.get("/api/relatos", response_model=list[Relato], tags=["relatos"])
def listar_relatos(
    status: Optional[Status] = None,
    tipo: Optional[Tipo] = None,
    desde: Optional[datetime] = Query(default=None, description="ISO 8601; relatos atualizados a partir de"),
    limite: int = Query(default=500, ge=1, le=1000),
):
    sql = "SELECT * FROM relatos WHERE 1=1"
    params: list = []
    if status:
        sql += " AND status = ?"
        params.append(status.value)
    if tipo:
        sql += " AND tipo = ?"
        params.append(tipo.value)
    if desde:
        if desde.tzinfo is None:
            desde = desde.replace(tzinfo=timezone.utc)
        sql += " AND atualizado_em >= ?"
        params.append(desde.astimezone(timezone.utc).isoformat(timespec="seconds"))
    sql += " ORDER BY criado_em DESC LIMIT ?"
    params.append(limite)
    with db.conexao() as con:
        return [para_relato(r) for r in con.execute(sql, params).fetchall()]


@app.get("/api/relatos/{relato_id}", response_model=RelatoDetalhe, tags=["relatos"])
def obter_relato(relato_id: int):
    with db.conexao() as con:
        row = con.execute("SELECT * FROM relatos WHERE id = ?", (relato_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Relato não encontrado.")
        hist = con.execute(
            "SELECT status, nota, autor, em FROM historico WHERE relato_id = ? ORDER BY id", (relato_id,)
        ).fetchall()
    d = para_relato(row)
    d["historico"] = [dict(h) for h in hist]
    return d


@app.post("/api/relatos", response_model=Relato, status_code=201, tags=["relatos"])
def criar_relato(
    entrada: RelatoEntrada,
    request: Request,
    x_api_key: str = Header(default=""),
):
    if entrada.origem == Origem.robo:
        if not token_valido(x_api_key, ROBO_TOKEN):
            raise HTTPException(status_code=401, detail="Token do robô inválido ou ausente.")
    else:
        limitador.verificar(request)
    ts = db.agora()
    with db.conexao() as con:
        cur = con.execute(
            "INSERT INTO relatos (tipo, descricao, lat, lon, origem, criado_em, atualizado_em)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (entrada.tipo.value, entrada.descricao, entrada.lat, entrada.lon, entrada.origem.value, ts, ts),
        )
        con.execute(
            "INSERT INTO historico (relato_id, status, nota, autor, em) VALUES (?, 'novo', 'Relato criado', ?, ?)",
            (cur.lastrowid, "robo" if entrada.origem == Origem.robo else "cidadao", ts),
        )
        row = con.execute("SELECT * FROM relatos WHERE id = ?", (cur.lastrowid,)).fetchone()
    log.info("relato criado id=%s tipo=%s origem=%s", row["id"], row["tipo"], row["origem"])
    return para_relato(row)


@app.post("/api/relatos/{relato_id}/confirmar", response_model=Relato, tags=["relatos"])
def confirmar_relato(relato_id: int, request: Request):
    """'Também vi isso': outra pessoa confirma que o obstáculo existe."""
    limitador.verificar(request)
    with db.conexao() as con:
        cur = con.execute(
            "UPDATE relatos SET confirmacoes = confirmacoes + 1 WHERE id = ?", (relato_id,)
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Relato não encontrado.")
        row = con.execute("SELECT * FROM relatos WHERE id = ?", (relato_id,)).fetchone()
    return para_relato(row)


@app.patch("/api/relatos/{relato_id}", response_model=RelatoDetalhe, tags=["integração RPA"])
def atualizar_status(relato_id: int, entrada: AtualizacaoStatus, autor: str = Depends(exigir_token_rpa)):
    """Usado pelo bot de RPA: prioriza, deduplica e registra o protocolo do chamado."""
    ts = db.agora()
    with db.conexao() as con:
        atual = con.execute("SELECT * FROM relatos WHERE id = ?", (relato_id,)).fetchone()
        if not atual:
            raise HTTPException(status_code=404, detail="Relato não encontrado.")
        con.execute(
            "UPDATE relatos SET status = ?, prioridade = COALESCE(?, prioridade),"
            " protocolo = COALESCE(?, protocolo), atualizado_em = ? WHERE id = ?",
            (
                entrada.status.value,
                entrada.prioridade.value if entrada.prioridade else None,
                entrada.protocolo,
                ts,
                relato_id,
            ),
        )
        nota = entrada.nota or (f"Protocolo {entrada.protocolo}" if entrada.protocolo else None)
        con.execute(
            "INSERT INTO historico (relato_id, status, nota, autor, em) VALUES (?, ?, ?, ?, ?)",
            (relato_id, entrada.status.value, nota, autor, ts),
        )
    log.info("status atualizado id=%s status=%s autor=%s", relato_id, entrada.status.value, autor)
    return obter_relato(relato_id)


@app.get("/api/estatisticas", tags=["indicadores"])
def estatisticas():
    """Indicadores de impacto exibidos na página inicial e usados no pitch."""
    with db.conexao() as con:
        total = con.execute("SELECT COUNT(*) FROM relatos").fetchone()[0]
        por_status = {
            r["status"]: r["n"]
            for r in con.execute("SELECT status, COUNT(*) AS n FROM relatos GROUP BY status")
        }
        por_tipo = [
            {"tipo": r["tipo"], "rotulo": ROTULOS_TIPO.get(r["tipo"], r["tipo"]), "total": r["n"]}
            for r in con.execute("SELECT tipo, COUNT(*) AS n FROM relatos GROUP BY tipo ORDER BY n DESC")
        ]
        confirmacoes = con.execute("SELECT COALESCE(SUM(confirmacoes), 0) FROM relatos").fetchone()[0]
    resolvidos = por_status.get("resolvido", 0)
    validos = total - por_status.get("duplicado", 0)
    return {
        "total": total,
        "por_status": por_status,
        "por_tipo": por_tipo,
        "confirmacoes": confirmacoes,
        "percentual_resolvidos": round(100 * resolvidos / validos, 1) if validos else 0.0,
    }


@app.exception_handler(Exception)
async def erro_inesperado(_: Request, exc: Exception):
    log.error("erro inesperado: %s", type(exc).__name__)
    return Response(
        content='{"detail":"Erro interno. Tente novamente."}', status_code=500, media_type="application/json"
    )

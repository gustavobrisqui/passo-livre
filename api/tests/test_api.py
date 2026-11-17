import importlib
import os

import pytest
from fastapi.testclient import TestClient

RPA = "token-rpa-de-teste"
ROBO = "token-robo-de-teste"


@pytest.fixture()
def cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "teste.db"))
    monkeypatch.setenv("RPA_TOKEN", RPA)
    monkeypatch.setenv("ROBO_TOKEN", ROBO)
    monkeypatch.setenv("SEED_DEMO", "true")
    monkeypatch.setenv("RATE_LIMIT_POR_MINUTO", "3")
    import app.main as main

    importlib.reload(main)
    with TestClient(main.app) as c:
        yield c


NOVO = {"tipo": "buraco", "descricao": "  Buraco   na calçada ", "lat": -23.5614, "lon": -46.6559}


def test_healthz_e_versao(cliente):
    assert cliente.get("/healthz").json() == {"status": "ok"}
    assert "versao" in cliente.get("/version").json()


def test_seed_popula_banco_vazio(cliente):
    relatos = cliente.get("/api/relatos").json()
    assert len(relatos) == 20
    assert all(r["simulado"] for r in relatos)


def test_criar_e_listar_relato(cliente):
    r = cliente.post("/api/relatos", json=NOVO)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["status"] == "novo"
    assert corpo["descricao"] == "Buraco na calçada"
    assert corpo["simulado"] is False
    novos = cliente.get("/api/relatos", params={"status": "novo"}).json()
    assert corpo["id"] in [x["id"] for x in novos]


@pytest.mark.parametrize(
    "alteracao",
    [{"lat": -22.9}, {"lon": -43.2}, {"tipo": "inexistente"}, {"descricao": "x" * 281}],
)
def test_validacao_rejeita_entrada_invalida(cliente, alteracao):
    assert cliente.post("/api/relatos", json={**NOVO, **alteracao}).status_code == 422


def test_rate_limit(cliente):
    codigos = [cliente.post("/api/relatos", json=NOVO).status_code for _ in range(4)]
    assert codigos == [201, 201, 201, 429]


def test_patch_exige_token_rpa(cliente):
    alvo = cliente.post("/api/relatos", json=NOVO).json()["id"]
    corpo = {"status": "em_analise", "prioridade": "alta", "protocolo": "PL-2026-9999"}
    assert cliente.patch(f"/api/relatos/{alvo}", json=corpo).status_code == 401
    errado = {"Authorization": "Bearer errado"}
    assert cliente.patch(f"/api/relatos/{alvo}", json=corpo, headers=errado).status_code == 401
    ok = cliente.patch(f"/api/relatos/{alvo}", json=corpo, headers={"Authorization": f"Bearer {RPA}"})
    assert ok.status_code == 200
    d = ok.json()
    assert (d["status"], d["prioridade"], d["protocolo"]) == ("em_analise", "alta", "PL-2026-9999")
    assert [h["autor"] for h in d["historico"]] == ["cidadao", "rpa"]


def test_robo_exige_token(cliente):
    robo = {**NOVO, "origem": "robo"}
    assert cliente.post("/api/relatos", json=robo).status_code == 401
    r = cliente.post("/api/relatos", json=robo, headers={"X-Api-Key": ROBO})
    assert r.status_code == 201 and r.json()["origem"] == "robo"


def test_confirmar_relato(cliente):
    alvo = cliente.post("/api/relatos", json=NOVO).json()
    r = cliente.post(f"/api/relatos/{alvo['id']}/confirmar")
    assert r.json()["confirmacoes"] == alvo["confirmacoes"] + 1
    assert cliente.post("/api/relatos/999999/confirmar").status_code == 404


def test_estatisticas(cliente):
    e = cliente.get("/api/estatisticas").json()
    assert e["total"] == 20
    assert 0 <= e["percentual_resolvidos"] <= 100


def test_metricas_prometheus(cliente):
    cliente.get("/api/relatos")
    texto = cliente.get("/metrics").text
    assert "passolivre_http_request_duration_seconds" in texto or "http_request_duration" in texto


def test_sem_token_configurado_ninguem_autoriza(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setenv("RPA_TOKEN", "")
    import app.main as main

    importlib.reload(main)
    with TestClient(main.app) as c:
        r = c.patch("/api/relatos/1", json={"status": "resolvido"}, headers={"Authorization": "Bearer "})
        assert r.status_code == 401
    os.environ.pop("RPA_TOKEN", None)

"""Dados de demonstração SIMULADOS (documentados em docs/dados-simulados.md).

Pontos próximos a locais reais de São Paulo, com tipos e status variados, para que o mapa
não comece vazio. Todo registro gerado aqui tem simulado=1 e aparece marcado na interface.
"""

from datetime import datetime, timedelta, timezone

from .db import conexao

# (tipo, descrição, lat, lon, status, prioridade, protocolo, dias atrás)
RELATOS_SIMULADOS = [
    ("buraco", "Buraco grande na calçada em frente ao ponto de ônibus", -23.56145, -46.65590, "em_analise", "alta", "PL-2026-0001", 6),
    ("carro_na_calcada", "Carros estacionados bloqueando a passagem toda manhã", -23.55780, -46.66210, "novo", None, None, 1),
    ("degrau_sem_rampa", "Esquina sem rebaixamento de guia para cadeira de rodas", -23.55052, -46.63331, "encaminhado", "alta", "PL-2026-0002", 12),
    ("entulho", "Entulho de obra ocupando metade da calçada", -23.54330, -46.64250, "resolvido", "media", "PL-2026-0003", 20),
    ("ponto_onibus_inacessivel", "Ponto sem abrigo e com degrau alto para embarcar", -23.58810, -46.63260, "em_analise", "alta", "PL-2026-0004", 4),
    ("buraco", "Piso tátil quebrado e buraco perto da estação", -23.53390, -46.62520, "novo", None, None, 2),
    ("calcada_estreita", "Calçada com menos de 1 metro por causa de poste e lixeira", -23.56960, -46.69190, "novo", None, None, 3),
    ("degrau_sem_rampa", "Entrada do posto de saúde só por escada", -23.52540, -46.71930, "encaminhado", "alta", "PL-2026-0005", 9),
    ("carro_na_calcada", "Motos estacionadas sobre a calçada em frente ao mercado", -23.61720, -46.66570, "resolvido", "media", "PL-2026-0006", 25),
    ("arvore_raiz", "Raiz de árvore levantou o piso, risco de queda", -23.58620, -46.68250, "em_analise", "media", "PL-2026-0007", 7),
    ("entulho", "Sacos de lixo e móveis velhos bloqueando a rampa", -23.49910, -46.62260, "novo", None, None, 1),
    ("ponto_onibus_inacessivel", "Ponto de ônibus sem calçada, embarque na terra", -23.65480, -46.71190, "novo", None, None, 5),
    ("buraco", "Tampa de bueiro afundada no meio da faixa de pedestres", -23.54720, -46.57420, "encaminhado", "alta", "PL-2026-0008", 11),
    ("iluminacao", "Trecho sem iluminação à noite, perigoso para idosos", -23.60230, -46.60180, "novo", None, None, 2),
    ("calcada_estreita", "Banca e cavaletes deixam só 60 cm para passar", -23.54480, -46.63890, "em_analise", "media", "PL-2026-0009", 3),
    ("degrau_sem_rampa", "Rampa existe mas termina em degrau de 15 cm", -23.56320, -46.65430, "resolvido", "alta", "PL-2026-0010", 30),
    ("arvore_raiz", "Calçada ondulada por raízes em toda a quadra", -23.52990, -46.66800, "novo", None, None, 4),
    ("carro_na_calcada", "Caminhão de entrega parado na calçada e na rampa", -23.59430, -46.68870, "novo", None, None, 1),
    ("outro", "Semáforo de pedestre sem sinal sonoro", -23.55690, -46.66100, "encaminhado", "media", "PL-2026-0011", 14),
    ("iluminacao", "Ponto de ônibus escuro, sem luz no abrigo", -23.63880, -46.64230, "novo", None, None, 6),
]


# Exemplos do robô de vistoria (Maker Lab), também SIMULADOS: mostram como os relatos enviados
# pelo robô (POST /api/relatos com origem=robo) aparecem no mapa, com o selo "🤖 robô".
# (tipo, descrição, lat, lon, status, dias atrás)
RELATOS_ROBO_SIMULADOS = [
    ("entulho", "Obstáculo a 18 cm detectado pelo sensor ultrassônico na faixa livre da calçada", -23.55780, -46.63950, "novo", 1),
    ("calcada_estreita", "Passagem com 70 cm de largura medida pelo robô de vistoria", -23.56490, -46.65280, "novo", 2),
    ("degrau_sem_rampa", "Desnível de 12 cm detectado no acesso à travessia", -23.54210, -46.63480, "em_analise", 3),
]


def garantir_exemplos_robo() -> int:
    """Insere os exemplos simulados do robô se ainda não houver nenhum (também em bancos já populados)."""
    with conexao() as con:
        existe = con.execute(
            "SELECT COUNT(*) FROM relatos WHERE origem = 'robo' AND simulado = 1"
        ).fetchone()[0]
        if existe:
            return 0
        base = datetime.now(timezone.utc).replace(microsecond=0)
        for tipo, desc, lat, lon, status, dias in RELATOS_ROBO_SIMULADOS:
            criado = (base - timedelta(days=dias)).isoformat()
            cur = con.execute(
                "INSERT INTO relatos (tipo, descricao, lat, lon, status, origem, simulado, criado_em, atualizado_em)"
                " VALUES (?, ?, ?, ?, ?, 'robo', 1, ?, ?)",
                (tipo, desc, lat, lon, status, criado, criado),
            )
            con.execute(
                "INSERT INTO historico (relato_id, status, nota, autor, em) VALUES (?, 'novo', ?, 'robo', ?)",
                (cur.lastrowid, "Detectado pelo robô de vistoria (dado simulado)", criado),
            )
        return len(RELATOS_ROBO_SIMULADOS)


def popular_se_vazio() -> int:
    """Insere os relatos simulados apenas se o banco estiver vazio. Retorna quantos inseriu."""
    with conexao() as con:
        total = con.execute("SELECT COUNT(*) FROM relatos").fetchone()[0]
        if total:
            return 0
        base = datetime.now(timezone.utc).replace(microsecond=0)
        for tipo, desc, lat, lon, status, prio, proto, dias in RELATOS_SIMULADOS:
            criado = (base - timedelta(days=dias)).isoformat()
            cur = con.execute(
                "INSERT INTO relatos (tipo, descricao, lat, lon, status, prioridade, protocolo, origem,"
                " confirmacoes, simulado, criado_em, atualizado_em)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, 'app', ?, 1, ?, ?)",
                (tipo, desc, lat, lon, status, prio, proto, dias % 7, criado, criado),
            )
            con.execute(
                "INSERT INTO historico (relato_id, status, nota, autor, em) VALUES (?, 'novo', ?, 'cidadao', ?)",
                (cur.lastrowid, "Relato criado (dado simulado)", criado),
            )
            if status != "novo":
                con.execute(
                    "INSERT INTO historico (relato_id, status, nota, autor, em) VALUES (?, ?, ?, 'rpa', ?)",
                    (cur.lastrowid, status, f"Protocolo {proto} (dado simulado)", criado),
                )
        return len(RELATOS_SIMULADOS)

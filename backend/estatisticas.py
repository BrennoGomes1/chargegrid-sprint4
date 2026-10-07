"""Estatísticas e relatório das sessões."""
from datetime import datetime

from .algoritmos import CAMPOS_ORDENACAO, merge_sort
from .modelos import Sessao


def calcular_estatisticas(sessoes: list[Sessao]) -> dict:
    """Calcula todas as estatísticas em UMA passada pela lista: O(n)."""
    total = len(sessoes)
    if total == 0:
        return {"total_sessoes": 0, "energia_total_kwh": 0, "receita_total": 0,
                "energia_media_kwh": 0, "duracao_media_min": 0, "sessoes_ponta": 0,
                "percentual_ponta": 0, "maior_consumo": None, "por_carregador": {}}

    energia_total = 0.0
    receita_total = 0.0
    duracao_total = 0
    sessoes_ponta = 0
    maior = sessoes[0]
    por_carregador: dict[str, dict] = {}

    for s in sessoes:
        energia_total += s.energia_kwh
        receita_total += s.valor_total
        duracao_total += s.duracao_min
        if s.horario == "ponta":
            sessoes_ponta += 1
        if s.energia_kwh > maior.energia_kwh:
            maior = s
        dados = por_carregador.setdefault(s.carregador, {"sessoes": 0, "energia_kwh": 0.0, "receita": 0.0})
        dados["sessoes"] += 1
        dados["energia_kwh"] += s.energia_kwh
        dados["receita"] += s.valor_total

    for dados in por_carregador.values():
        dados["energia_kwh"] = round(dados["energia_kwh"], 2)
        dados["receita"] = round(dados["receita"], 2)

    return {
        "total_sessoes": total,
        "energia_total_kwh": round(energia_total, 2),
        "receita_total": round(receita_total, 2),
        "energia_media_kwh": round(energia_total / total, 2),
        "duracao_media_min": round(duracao_total / total),
        "sessoes_ponta": sessoes_ponta,
        "percentual_ponta": round(sessoes_ponta / total * 100, 1),
        "maior_consumo": maior.para_dict(),
        "por_carregador": dict(sorted(por_carregador.items())),
    }


def _reais(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _num(valor: float, casas: int = 2) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_relatorio(sessoes: list[Sessao]) -> dict:
    """Resumo final: estatísticas + as 3 sessões de maior receita (via Merge Sort)."""
    est = calcular_estatisticas(sessoes)
    ordenadas, _ = merge_sort(sessoes, CAMPOS_ORDENACAO["valor_total"], decrescente=True)
    top = ordenadas[:3]
    agora = datetime.now()

    linhas = [
        "RELATÓRIO DE RECARGAS, CHARGEGRID INTELLIGENCE",
        f"Gerado em {agora:%d/%m/%Y às %H:%M}",
        "",
        f"Sessões registradas: {est['total_sessoes']}",
        f"Energia entregue: {_num(est['energia_total_kwh'])} kWh",
        f"Receita total: {_reais(est['receita_total'])}",
        f"Consumo médio por sessão: {_num(est['energia_media_kwh'])} kWh",
        f"Duração média: {est['duracao_media_min']} min",
        f"Sessões no horário de ponta: {est['sessoes_ponta']} ({_num(est['percentual_ponta'], 1)}%)",
        "",
        "Por carregador:",
    ]
    for carregador, d in est["por_carregador"].items():
        linhas.append(f"  {carregador}: {d['sessoes']} sessões, {_num(d['energia_kwh'])} kWh, {_reais(d['receita'])}")
    if top:
        linhas += ["", "Sessões de maior receita:"]
        for s in top:
            linhas.append(f"  #{s.id} {s.placa} no {s.carregador}: {_num(s.energia_kwh)} kWh, {_reais(s.valor_total)}")

    return {
        "gerado_em": agora.isoformat(timespec="minutes"),
        "estatisticas": est,
        "top_receita": [s.para_dict() for s in top],
        "texto": "\n".join(linhas),
    }

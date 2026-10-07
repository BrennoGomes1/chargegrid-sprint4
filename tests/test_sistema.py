from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from backend.algoritmos import (CAMPOS_ORDENACAO, bubble_sort, busca_binaria_por_id,
                                busca_hash_por_id, busca_linear, busca_linear_por_id, merge_sort)
from backend.dados_exemplo import gerar_lista
from backend.main import app, repo
from backend.tarifacao import calcular_tarifacao


@pytest.fixture
def sessoes():
    return gerar_lista(60)


@pytest.mark.parametrize("campo", list(CAMPOS_ORDENACAO))
@pytest.mark.parametrize("decrescente", [False, True])
def test_ordenacoes_iguais_ao_sorted(sessoes, campo, decrescente):
    chave = CAMPOS_ORDENACAO[campo]
    esperado = [chave(s) for s in sorted(sessoes, key=chave, reverse=decrescente)]
    for funcao in (merge_sort, bubble_sort):
        ordenadas, _ = funcao(sessoes, chave, decrescente)
        assert [chave(s) for s in ordenadas] == esperado


def test_buscas_por_id(sessoes):
    indice = {s.id: s for s in sessoes}
    for alvo in (1, 30, 60):
        assert busca_linear_por_id(sessoes, alvo)[0].id == alvo
        assert busca_binaria_por_id(sessoes, alvo)[0].id == alvo
        assert busca_hash_por_id(indice, alvo)[0].id == alvo
    assert busca_binaria_por_id(sessoes, 999)[0] is None
    assert busca_linear_por_id(sessoes, 999) == (None, 60)


def test_busca_linear_por_placa(sessoes):
    placa = sessoes[10].placa
    resultados, comparacoes = busca_linear(sessoes, "placa", placa.lower())
    assert sessoes[10] in resultados and comparacoes == len(sessoes)


def test_tarifacao():
    ponta = calcular_tarifacao(datetime(2026, 9, 25, 18, 30), 10)
    fora = calcular_tarifacao(datetime(2026, 9, 25, 10, 0), 10)
    assert ponta["valor_total"] == 21.0 and fora["valor_total"] == 14.5


def test_api_fluxo_completo():
    repo.limpar()
    cliente = TestClient(app)
    r = cliente.post("/api/sessoes", json={"carregador": "CG-01", "placa": "abc1d23",
                                           "inicio": "2026-09-25T18:30", "fim": "2026-09-25T19:15",
                                           "energia_kwh": 10})
    assert r.status_code == 201 and r.json()["valor_total"] == 21.0
    assert cliente.post("/api/sessoes", json={"carregador": "CG-01", "placa": "X",
                                              "inicio": "2026-09-25T18:30", "fim": "2026-09-25T19:15",
                                              "energia_kwh": 10}).status_code == 422
    cliente.post("/api/sessoes/exemplo?quantidade=9")
    assert cliente.get("/api/sessoes").json()["total"] == 10
    assert cliente.get("/api/sessoes/busca", params={"campo": "placa", "valor": "ABC1D23"}).json()["comparacoes"] == 10
    assert cliente.get("/api/sessoes/busca-id", params={"id": 7, "metodo": "binaria"}).json()["sessoes"][0]["id"] == 7
    assert cliente.get("/api/sessoes/ordenadas", params={"algoritmo": "bubble"}).json()["n"] == 10
    assert cliente.get("/api/estatisticas").json()["total_sessoes"] == 10
    assert "RELATÓRIO" in cliente.get("/api/relatorio").json()["texto"]
    assert len(cliente.get("/api/benchmark?tamanhos=10,20").json()["resultados"]) == 2
    assert cliente.get("/").status_code in (200, 404)
    repo.limpar()

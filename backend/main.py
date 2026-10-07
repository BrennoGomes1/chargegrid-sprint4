"""API do ChargeGrid Intelligence (FastAPI).

Fluxo: interface (fetch) -> rota da API -> repositório/algoritmos em Python
-> resposta JSON -> interface renderiza o resultado.

Rodar:  uvicorn backend.main:app --reload
"""
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .algoritmos import (CAMPOS_ORDENACAO, bubble_sort, busca_binaria_por_id,
                         busca_hash_por_id, busca_linear, busca_linear_por_id, merge_sort)
from .benchmark import executar as executar_benchmark
from .dados_exemplo import popular
from .estatisticas import calcular_estatisticas, gerar_relatorio
from .repositorio import RepositorioSessoes

app = FastAPI(title="ChargeGrid Intelligence")
repo = RepositorioSessoes()
PAGINA = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


class NovaSessao(BaseModel):
    carregador: str
    placa: str
    inicio: datetime
    fim: datetime
    energia_kwh: float = Field(gt=0, le=200)


def _dicts(sessoes):
    return [s.para_dict() for s in sessoes]


@app.get("/", include_in_schema=False)
def pagina():
    return FileResponse(PAGINA)


@app.get("/api/sessoes")
def listar_sessoes():
    return {"total": len(repo), "sessoes": _dicts(repo.sessoes)}


@app.post("/api/sessoes", status_code=201)
def registrar_sessao(dados: NovaSessao):
    try:
        sessao = repo.adicionar(**dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro))
    return sessao.para_dict()


@app.post("/api/sessoes/exemplo", status_code=201)
def carregar_exemplo(quantidade: int = Query(10, ge=1, le=200)):
    popular(repo, quantidade)
    return {"total": len(repo)}


@app.delete("/api/sessoes")
def apagar_sessoes():
    repo.limpar()
    return {"total": 0}


@app.get("/api/sessoes/busca")
def buscar(campo: Literal["placa", "carregador"], valor: str):
    resultados, comparacoes = busca_linear(repo.sessoes, campo, valor)
    return {"algoritmo": "Busca linear", "complexidade": "O(n)", "n": len(repo),
            "comparacoes": comparacoes, "sessoes": _dicts(resultados)}


@app.get("/api/sessoes/busca-id")
def buscar_por_id(id: int, metodo: Literal["linear", "binaria", "hash"] = "linear"):
    if metodo == "linear":
        sessao, comparacoes = busca_linear_por_id(repo.sessoes, id)
        nome, complexidade = "Busca linear", "O(n)"
    elif metodo == "binaria":
        sessao, comparacoes = busca_binaria_por_id(repo.sessoes, id)
        nome, complexidade = "Busca binária", "O(log n)"
    else:
        sessao, comparacoes = busca_hash_por_id(repo.indice, id)
        nome, complexidade = "Tabela hash (dict)", "O(1)"
    return {"algoritmo": nome, "complexidade": complexidade, "n": len(repo),
            "comparacoes": comparacoes, "sessoes": _dicts([sessao] if sessao else [])}


@app.get("/api/sessoes/ordenadas")
def ordenar(campo: Literal["energia_kwh", "valor_total", "inicio", "duracao_min", "placa"] = "energia_kwh",
            ordem: Literal["asc", "desc"] = "desc",
            algoritmo: Literal["merge", "bubble"] = "merge"):
    funcao = merge_sort if algoritmo == "merge" else bubble_sort
    ordenadas, comparacoes = funcao(repo.sessoes, CAMPOS_ORDENACAO[campo], decrescente=(ordem == "desc"))
    nome, complexidade = ("Merge sort", "O(n log n)") if algoritmo == "merge" else ("Bubble sort", "O(n²)")
    return {"algoritmo": nome, "complexidade": complexidade, "n": len(repo),
            "comparacoes": comparacoes, "sessoes": _dicts(ordenadas)}


@app.get("/api/estatisticas")
def estatisticas():
    return calcular_estatisticas(repo.sessoes)


@app.get("/api/relatorio")
def relatorio():
    return gerar_relatorio(repo.sessoes)


@app.get("/api/benchmark")
def benchmark(tamanhos: str = "100,500,1000,2000"):
    try:
        lista = [int(t) for t in tamanhos.split(",") if t.strip()][:6]
    except ValueError:
        raise HTTPException(status_code=422, detail="Informe os tamanhos como números separados por vírgula.")
    if not lista or any(n < 1 or n > 3000 for n in lista):
        raise HTTPException(status_code=422, detail="Use tamanhos entre 1 e 3000.")
    return {"resultados": executar_benchmark(lista)}

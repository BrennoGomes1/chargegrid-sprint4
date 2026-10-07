"""Compara o número de operações dos algoritmos conforme n cresce.

Rode no terminal com:  python -m backend.benchmark
"""
import time

from .algoritmos import (CAMPOS_ORDENACAO, bubble_sort, busca_binaria_por_id,
                         busca_hash_por_id, busca_linear_por_id, merge_sort)
from .dados_exemplo import gerar_lista

TAMANHOS_PADRAO = (100, 500, 1000, 2000)


def _medir(funcao):
    inicio = time.perf_counter()
    _, comparacoes = funcao()
    return {"comparacoes": comparacoes, "ms": round((time.perf_counter() - inicio) * 1000, 3)}


def executar(tamanhos=TAMANHOS_PADRAO) -> list[dict]:
    linhas = []
    for n in tamanhos:
        sessoes = gerar_lista(n)
        indice = {s.id: s for s in sessoes}
        alvo = n  # último id: pior caso da busca linear
        chave = CAMPOS_ORDENACAO["energia_kwh"]
        linhas.append({
            "n": n,
            "busca_linear": _medir(lambda: busca_linear_por_id(sessoes, alvo)),
            "busca_binaria": _medir(lambda: busca_binaria_por_id(sessoes, alvo)),
            "busca_hash": _medir(lambda: busca_hash_por_id(indice, alvo)),
            "merge_sort": _medir(lambda: merge_sort(sessoes, chave)),
            "bubble_sort": _medir(lambda: bubble_sort(sessoes, chave)),
        })
    return linhas


if __name__ == "__main__":
    colunas = ("busca_hash", "busca_binaria", "busca_linear", "merge_sort", "bubble_sort")
    print(f"{'n':>6} | " + " | ".join(f"{c:>13}" for c in colunas))
    print("-" * 85)
    for linha in executar():
        print(f"{linha['n']:>6} | " + " | ".join(f"{linha[c]['comparacoes']:>13,}" for c in colunas))
    print("\nValores = número de comparações. Busca linear medida no pior caso (último id).")

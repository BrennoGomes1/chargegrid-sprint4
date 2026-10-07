"""Algoritmos de busca e ordenação implementados pelo grupo.

Cada função devolve também a quantidade de comparações feitas, para que a
interface mostre como o número de operações cresce com o número de sessões.
"""
from typing import Callable

from .modelos import Sessao

# Campos que a interface pode usar para ordenar: nome -> função que extrai a chave
CAMPOS_ORDENACAO: dict[str, Callable[[Sessao], object]] = {
    "energia_kwh": lambda s: s.energia_kwh,
    "valor_total": lambda s: s.valor_total,
    "inicio": lambda s: s.inicio,
    "duracao_min": lambda s: s.duracao_min,
    "placa": lambda s: s.placa,
}


# ---------------------------------------------------------------- BUSCAS

def busca_linear(sessoes: list[Sessao], campo: str, valor: str) -> tuple[list[Sessao], int]:
    """Busca linear por placa ou carregador.

    Percorre a lista do primeiro ao último elemento comparando o campo com o
    valor procurado. Como pode haver mais de uma sessão com a mesma placa,
    ela não para no primeiro acerto: sempre olha as n sessões.
    Complexidade: O(n).
    """
    alvo = valor.strip().upper().replace("-", "")
    resultados: list[Sessao] = []
    comparacoes = 0
    for sessao in sessoes:
        comparacoes += 1
        if getattr(sessao, campo).upper() == alvo:
            resultados.append(sessao)
    return resultados, comparacoes


def busca_linear_por_id(sessoes: list[Sessao], id_alvo: int) -> tuple[Sessao | None, int]:
    """Busca linear por id: para assim que encontra.

    Melhor caso: o id é o primeiro da lista (1 comparação, O(1)).
    Pior caso: o id é o último ou não existe (n comparações, O(n)).
    """
    comparacoes = 0
    for sessao in sessoes:
        comparacoes += 1
        if sessao.id == id_alvo:
            return sessao, comparacoes
    return None, comparacoes


def busca_binaria_por_id(sessoes: list[Sessao], id_alvo: int) -> tuple[Sessao | None, int]:
    """Busca binária por id.

    Pré-requisito: lista ordenada por id (garantido pelo repositório, que
    gera ids crescentes). A cada passo olhamos o elemento do meio e
    descartamos metade da lista. Termina quando acha o id ou quando o
    intervalo fica vazio (inicio > fim).
    Complexidade: O(log n).
    """
    inicio, fim = 0, len(sessoes) - 1
    comparacoes = 0
    while inicio <= fim:
        meio = (inicio + fim) // 2
        comparacoes += 1
        id_meio = sessoes[meio].id
        if id_meio == id_alvo:
            return sessoes[meio], comparacoes
        if id_meio < id_alvo:
            inicio = meio + 1   # o alvo está na metade da direita
        else:
            fim = meio - 1      # o alvo está na metade da esquerda
    return None, comparacoes


def busca_hash_por_id(indice: dict[int, Sessao], id_alvo: int) -> tuple[Sessao | None, int]:
    """Acesso direto pelo dicionário (tabela hash).

    O Python calcula o hash do id e vai direto à posição: 1 operação,
    independente de n. Complexidade: O(1) no caso médio.
    """
    return indice.get(id_alvo), 1


# ------------------------------------------------------------ ORDENAÇÃO

def merge_sort(sessoes: list[Sessao], chave: Callable[[Sessao], object],
               decrescente: bool = False) -> tuple[list[Sessao], int]:
    """Merge Sort (algoritmo principal de ordenação do sistema).

    1. Divide a lista ao meio recursivamente até sobrarem listas de 1 elemento.
    2. Intercala (merge) as metades já ordenadas, comparando sempre o primeiro
       elemento de cada uma e levando o menor (ou maior) para o resultado.
    São log n níveis de divisão e cada nível faz no máximo n comparações.
    Complexidade: O(n log n) em todos os casos. Não altera a lista original.
    """
    contador = [0]

    def ordenar(lista: list[Sessao]) -> list[Sessao]:
        if len(lista) <= 1:
            return lista
        meio = len(lista) // 2
        esquerda = ordenar(lista[:meio])
        direita = ordenar(lista[meio:])
        return intercalar(esquerda, direita)

    def intercalar(esquerda: list[Sessao], direita: list[Sessao]) -> list[Sessao]:
        resultado: list[Sessao] = []
        i = j = 0
        while i < len(esquerda) and j < len(direita):
            contador[0] += 1
            a, b = chave(esquerda[i]), chave(direita[j])
            vem_da_esquerda = a >= b if decrescente else a <= b
            if vem_da_esquerda:
                resultado.append(esquerda[i])
                i += 1
            else:
                resultado.append(direita[j])
                j += 1
        # Uma das metades acabou: o que sobrou na outra já está ordenado
        resultado.extend(esquerda[i:])
        resultado.extend(direita[j:])
        return resultado

    return ordenar(list(sessoes)), contador[0]


def bubble_sort(sessoes: list[Sessao], chave: Callable[[Sessao], object],
                decrescente: bool = False) -> tuple[list[Sessao], int]:
    """Bubble Sort (implementado para comparação com o Merge Sort).

    Compara pares vizinhos e troca os que estão fora de ordem. A cada
    passada, o maior (ou menor) elemento "borbulha" para o fim. Se uma
    passada inteira não fizer troca, a lista já está ordenada e paramos.
    Complexidade: O(n²) no pior caso e no caso médio; O(n) no melhor caso.
    """
    lista = list(sessoes)
    n = len(lista)
    comparacoes = 0
    for passada in range(n - 1):
        houve_troca = False
        for j in range(n - 1 - passada):
            comparacoes += 1
            a, b = chave(lista[j]), chave(lista[j + 1])
            fora_de_ordem = a < b if decrescente else a > b
            if fora_de_ordem:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
                houve_troca = True
        if not houve_troca:
            break
    return lista, comparacoes

"""Armazenamento das sessões em memória."""
import re
from datetime import datetime

from .modelos import Sessao
from .tarifacao import calcular_tarifacao

CARREGADORES = ("CG-01", "CG-02", "CG-03", "CG-04")
PADRAO_PLACA = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")  # antiga ou Mercosul


def criar_sessao(id_: int, carregador: str, placa: str, inicio: datetime,
                 fim: datetime, energia_kwh: float) -> Sessao:
    """Valida os dados, calcula a tarifação e monta o objeto Sessao."""
    placa = placa.strip().upper().replace("-", "")
    if carregador not in CARREGADORES:
        raise ValueError(f"Carregador inválido. Use um de: {', '.join(CARREGADORES)}.")
    if not PADRAO_PLACA.match(placa):
        raise ValueError("Placa inválida. Use o formato ABC1234 ou ABC1D23.")
    if fim <= inicio:
        raise ValueError("O fim da sessão precisa ser depois do início.")
    if energia_kwh <= 0:
        raise ValueError("A energia entregue precisa ser maior que zero.")

    tarifa = calcular_tarifacao(inicio, energia_kwh)
    return Sessao(
        id=id_, carregador=carregador, placa=placa, inicio=inicio, fim=fim,
        energia_kwh=round(energia_kwh, 2), horario=tarifa["horario"],
        tarifa_kwh=tarifa["tarifa_kwh"], taxa_conexao=tarifa["taxa_conexao"],
        valor_total=tarifa["valor_total"],
    )


class RepositorioSessoes:
    """Guarda as sessões usando duas estruturas que apontam para os MESMOS objetos:

    - self.sessoes (list): mantém a ordem de chegada. Como os ids são gerados
      em ordem crescente, a lista já fica ordenada por id, o que permite
      busca binária sem precisar ordenar antes.
    - self.indice (dict id -> Sessao): tabela hash para acesso direto por id
      em O(1) no caso médio.
    """

    def __init__(self) -> None:
        self.sessoes: list[Sessao] = []
        self.indice: dict[int, Sessao] = {}
        self._proximo_id = 1

    def adicionar(self, carregador: str, placa: str, inicio: datetime,
                  fim: datetime, energia_kwh: float) -> Sessao:
        sessao = criar_sessao(self._proximo_id, carregador, placa, inicio, fim, energia_kwh)
        self.sessoes.append(sessao)       # O(1) amortizado
        self.indice[sessao.id] = sessao   # O(1) no caso médio
        self._proximo_id += 1
        return sessao

    def limpar(self) -> None:
        self.sessoes.clear()
        self.indice.clear()
        self._proximo_id = 1

    def __len__(self) -> int:
        return len(self.sessoes)

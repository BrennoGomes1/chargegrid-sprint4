"""Geração de sessões de exemplo para a demonstração e para o benchmark."""
import random
from datetime import datetime, timedelta

from .modelos import Sessao
from .repositorio import CARREGADORES, RepositorioSessoes, criar_sessao

LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
POTENCIAS_KW = (7.4, 11.0, 22.0)  # potências típicas de carregadores AC


def _placa_aleatoria(rng: random.Random) -> str:
    return ("".join(rng.choice(LETRAS) for _ in range(3)) + str(rng.randint(0, 9))
            + rng.choice(LETRAS) + f"{rng.randint(0, 99):02d}")


def _parametros_aleatorios(rng: random.Random, dia: datetime) -> dict:
    inicio = dia + timedelta(hours=rng.randint(6, 21), minutes=rng.choice((0, 10, 15, 20, 30, 40, 45, 50)))
    duracao = rng.randint(20, 150)
    energia = rng.choice(POTENCIAS_KW) * duracao / 60 * rng.uniform(0.7, 0.95)
    return {
        "carregador": rng.choice(CARREGADORES),
        "placa": _placa_aleatoria(rng),
        "inicio": inicio,
        "fim": inicio + timedelta(minutes=duracao),
        "energia_kwh": round(energia, 2),
    }


def _hoje() -> datetime:
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def popular(repo: RepositorioSessoes, quantidade: int = 10, semente: int | None = None) -> None:
    """Adiciona sessões de exemplo evitando que dois carros usem o mesmo carregador ao mesmo tempo."""
    rng = random.Random(semente)
    dia = _hoje()
    for _ in range(quantidade):
        for _tentativa in range(50):
            p = _parametros_aleatorios(rng, dia)
            ocupado = any(s.carregador == p["carregador"] and p["inicio"] < s.fim and s.inicio < p["fim"]
                          for s in repo.sessoes)
            if not ocupado:
                break
        repo.adicionar(**p)


def gerar_lista(n: int, semente: int = 42) -> list[Sessao]:
    """Lista independente do repositório, usada no benchmark."""
    rng = random.Random(semente)
    dia = _hoje()
    return [criar_sessao(i + 1, **_parametros_aleatorios(rng, dia)) for i in range(n)]

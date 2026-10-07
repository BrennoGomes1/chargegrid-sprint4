"""Regras de tarifação das sessões de recarga."""
from datetime import datetime

TAXA_CONEXAO = 2.50        # R$ fixo por sessão
TARIFA_FORA_PONTA = 1.20   # R$ por kWh
TARIFA_PONTA = 1.85        # R$ por kWh (horário de maior demanda na rede)
INICIO_PONTA = 18          # 18:00
FIM_PONTA = 21             # até 20:59


def eh_horario_de_ponta(momento: datetime) -> bool:
    return INICIO_PONTA <= momento.hour < FIM_PONTA


def calcular_tarifacao(inicio: datetime, energia_kwh: float) -> dict:
    """Calcula o valor de uma sessão.

    A tarifa é definida pelo horário de início: sessões que começam no horário
    de ponta pagam mais caro, o que incentiva recargas fora do pico da rede.
    Complexidade O(1): só comparações e contas, independente de quantas
    sessões existem.
    """
    ponta = eh_horario_de_ponta(inicio)
    tarifa = TARIFA_PONTA if ponta else TARIFA_FORA_PONTA
    valor_energia = round(energia_kwh * tarifa, 2)
    return {
        "horario": "ponta" if ponta else "fora de ponta",
        "tarifa_kwh": tarifa,
        "taxa_conexao": TAXA_CONEXAO,
        "valor_energia": valor_energia,
        "valor_total": round(valor_energia + TAXA_CONEXAO, 2),
    }

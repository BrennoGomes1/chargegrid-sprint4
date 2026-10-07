"""Estrutura de dados que representa uma sessão de recarga."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sessao:
    """Uma sessão de recarga de veículo elétrico.

    Escolhemos dataclass porque uma sessão é um registro com campos fixos e
    tipados. O Python gera __init__, __repr__ e __eq__ automaticamente, e o
    acesso é por nome (sessao.energia_kwh), o que deixa os algoritmos de busca
    e ordenação legíveis. Um dicionário também funcionaria, mas não garante
    que toda sessão tenha os mesmos campos.
    """

    id: int
    carregador: str       # ex.: "CG-01"
    placa: str            # ex.: "ABC1D23"
    inicio: datetime
    fim: datetime
    energia_kwh: float    # energia entregue ao veículo
    horario: str          # "ponta" ou "fora de ponta"
    tarifa_kwh: float     # R$/kWh aplicado
    taxa_conexao: float   # taxa fixa por sessão
    valor_total: float    # valor final cobrado

    @property
    def duracao_min(self) -> int:
        """Duração calculada a partir do início e do fim (não é armazenada)."""
        return int((self.fim - self.inicio).total_seconds() // 60)

    def para_dict(self) -> dict:
        """Converte a sessão em dicionário para enviar como JSON à interface."""
        return {
            "id": self.id,
            "carregador": self.carregador,
            "placa": self.placa,
            "inicio": self.inicio.isoformat(timespec="minutes"),
            "fim": self.fim.isoformat(timespec="minutes"),
            "duracao_min": self.duracao_min,
            "energia_kwh": self.energia_kwh,
            "horario": self.horario,
            "tarifa_kwh": self.tarifa_kwh,
            "taxa_conexao": self.taxa_conexao,
            "valor_total": self.valor_total,
        }

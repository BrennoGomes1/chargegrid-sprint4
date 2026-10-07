# ChargeGrid Intelligence (Sprint 4)

**Disciplina:** Data Structures and Algorithms  
**Turma:** 1CCPX

| Integrante | RM |
|---|---|
| Brenno Ferreira Gomes dos Santos | 570525 |
| Eduardo Moreira Silva | 569923 |
| Enzo Stahal | 569001 |
| Matheus Bruno | 572944 |

Sistema de gerenciamento de sessões de recarga de veículos elétricos.
Backend em **Python (FastAPI)** e interface **Web** (HTML/CSS/JS) que consome a API via `fetch`.

## Como rodar

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Abra **http://localhost:8000**. A documentação automática da API fica em http://localhost:8000/docs.

Outros comandos:

```bash
python -m backend.benchmark   # tabela de comparações no terminal
python -m pytest -q           # testes automatizados
```

## Estrutura

```
backend/
  modelos.py        dataclass Sessao (estrutura de dados da sessão)
  tarifacao.py      cálculo do valor (ponta x fora de ponta + taxa fixa)
  repositorio.py    armazenamento: list (ordem de chegada) + dict (índice por id)
  algoritmos.py     busca linear, busca binária, busca por hash, Merge Sort, Bubble Sort
  estatisticas.py   estatísticas em uma passada O(n) e relatório final
  benchmark.py      compara o número de comparações conforme n cresce
  dados_exemplo.py  gera sessões de exemplo
  main.py           rotas da API e entrega da página
frontend/
  index.html        interface web
tests/
  test_sistema.py   testes dos algoritmos, da tarifação e da API
```

## Fluxo interface → backend

```
Interface (fetch) → rota FastAPI (main.py) → repositório / algoritmos (Python)
                  → resposta JSON → interface renderiza tabela, estatísticas e contadores
```

| Ação na interface | Rota | Código Python |
|---|---|---|
| Registrar sessão | `POST /api/sessoes` | `RepositorioSessoes.adicionar` + `calcular_tarifacao` |
| Listar | `GET /api/sessoes` | `repo.sessoes` |
| Buscar por placa/carregador | `GET /api/sessoes/busca` | `busca_linear` |
| Buscar por ID | `GET /api/sessoes/busca-id` | `busca_linear_por_id`, `busca_binaria_por_id`, `busca_hash_por_id` |
| Ordenar | `GET /api/sessoes/ordenadas` | `merge_sort`, `bubble_sort` |
| Estatísticas | `GET /api/estatisticas` | `calcular_estatisticas` |
| Relatório | `GET /api/relatorio` | `gerar_relatorio` |
| Comparar algoritmos | `GET /api/benchmark` | `benchmark.executar` |

## Algoritmos e complexidade

| Algoritmo | Onde | Complexidade | Por quê |
|---|---|---|---|
| Acesso por hash | `busca_hash_por_id` | O(1) | o dict vai direto à posição pelo hash do id |
| Busca binária | `busca_binaria_por_id` | O(log n) | descarta metade da lista a cada comparação |
| Busca linear | `busca_linear`, `busca_linear_por_id` | O(n) | pode precisar olhar todas as n sessões |
| Estatísticas | `calcular_estatisticas` | O(n) | uma única passada pela lista |
| Merge Sort | `merge_sort` | O(n log n) | log n níveis de divisão, até n comparações por nível |
| Bubble Sort | `bubble_sort` | O(n²) | até n passadas, cada uma com até n comparações |
| Tarifação | `calcular_tarifacao` | O(1) | só contas, independe de n |

Resultado do benchmark (comparações):

| n | Hash | Binária | Linear | Merge sort | Bubble sort |
|---:|---:|---:|---:|---:|---:|
| 100 | 1 | 7 | 100 | 537 | 4.814 |
| 500 | 1 | 9 | 500 | 3.844 | 124.735 |
| 1.000 | 1 | 10 | 1.000 | 8.690 | 499.485 |
| 2.000 | 1 | 11 | 2.000 | 19.404 | 1.998.010 |

## Tarifação

- Taxa de conexão: R$ 2,50 por sessão
- Fora de ponta: R$ 1,20/kWh
- Ponta (sessões que começam entre 18h e 20h59): R$ 1,85/kWh
- `valor = taxa + energia_kwh × tarifa`

As sessões ficam em memória: ao reiniciar o servidor os dados são apagados (persistência em banco é uma das evoluções futuras).

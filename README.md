# TaskAnalyzer

Projeto da entrega intermediária do Bootcamp III. A especificação SDD da fase 1 orienta a implementação de uma função que analisa tarefas concluídas, calcula tempo médio de conclusão e taxa de atraso e agrupa os resultados por prioridade. O código usa apenas a biblioteca padrão do Python; `pytest` é a única dependência de teste.

## Requisitos e execução

- Python 3.11 ou superior.
- Instalar as dependências em ambiente virtual:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

Em sistemas nos quais `venv` não inclui `pip`, é possível criar o ambiente com `uv venv .venv` e instalar com `uv pip install --python .venv/bin/python -r requirements.txt`.

Uso da interface pública:

```python
from datetime import datetime, timezone
from src.task_analyzer import analyze_tasks

utc = timezone.utc
tasks = [{
    "id_tarefa": 1,
    "data_criacao": datetime(2026, 9, 1, 8, tzinfo=utc),
    "data_inicio": datetime(2026, 9, 1, 9, tzinfo=utc),
    "data_conclusao": datetime(2026, 9, 1, 10, tzinfo=utc),
    "prazo": datetime(2026, 9, 1, 11, tzinfo=utc),
    "prioridade": "baixa",
    "status": "concluida",
}]

print(analyze_tasks(tasks))
```

A função recebe uma lista de dicionários e devolve contagens, médias em minutos e horas, taxa de atraso e indicadores para as três prioridades. Entradas inválidas geram `TaskValidationError`. O formato completo está em [specs/task_analyzer_spec.md](specs/task_analyzer_spec.md).

## Estrutura

```text
sdd-task-analyzer/
├── README.md
├── CONTEXT_RULES.md
├── .gitignore
├── requirements.txt
├── specs/
│   └── task_analyzer_spec.md
├── tests/
│   └── test_harness.py
└── src/
    └── task_analyzer.py
```

## Aderência ao contrato

A [especificação](specs/task_analyzer_spec.md) e as [regras de contexto](CONTEXT_RULES.md) foram transpostas dos materiais da fase 1. O enunciado da fase 2 alterou as unidades exigidas e o comportamento para ausência de tarefas concluídas válidas; a seção **Ajustes da fase 2** documenta a decisão aplicada no código e nos testes. Não há persistência de dados nem funcionalidades da fase 3.

## Status do build

Validação local em Python 3.12.3: `8 passed` com `.venv/bin/python -m pytest -q` em 17/10/2026. A fase 2 também exige repositório público, pelo menos um Pull Request documentado, vídeo de apresentação e PDF de submissão; esses itens dependem de publicação e gravação pelo estudante.

## Registro de uso da IA

O pedido à IA foi implementar `analyze_tasks` e `TaskValidationError` a partir de `CONTEXT_RULES.md` e `specs/task_analyzer_spec.md`, depois transformar os cenários de aceite em `tests/test_harness.py`. As regras limitaram a solução a Python 3.11+, biblioteca padrão para o módulo, funções tipadas, erros específicos e nenhuma persistência. A divergência entre as fases sobre unidades e ausência de tarefas válidas foi registrada na especificação antes da homologação pelos testes.

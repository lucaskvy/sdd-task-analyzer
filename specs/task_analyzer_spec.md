# Especificação SDD — TaskAnalyzer

Versão 1.0 (fase 1), com ajustes explícitos para a entrega intermediária (fase 2). Referência: `Especificacao SDD TaskAnalyzer - Lucas de Souza Batista.pdf` e `Desafio Etapa Intermediária Bootcamp III.pdf` fornecidos com o trabalho.

## Objetivo

Analisar tarefas estruturadas para calcular duração média de conclusão, taxa de atraso e indicadores por prioridade. O módulo apenas recebe dados e devolve métricas; não os persiste.

## Interface

`analyze_tasks(tasks: list[dict[str, object]]) -> dict[str, object]`

Cada tarefa é um dicionário com os campos abaixo:

| Campo | Tipo | Obrigatório | Regra |
| --- | --- | --- | --- |
| `id_tarefa` | `int` | Sim | Maior que zero e único na lista; `bool` não é aceito. |
| `data_criacao` | `datetime` | Sim | Data e hora com fuso UTC. |
| `data_inicio` | `datetime` ou `None` | Não | Data e hora com fuso UTC, quando presente. |
| `data_conclusao` | `datetime` ou `None` | Não | Data e hora com fuso UTC, quando presente. |
| `prazo` | `datetime` | Sim | Data e hora com fuso UTC. |
| `prioridade` | `str` | Sim | `baixa`, `media` ou `alta`. |
| `status` | `str` | Sim | `concluida`, `pendente` ou `cancelada`. |

Uma tarefa `concluida` exige `data_inicio` e `data_conclusao`. Campos ausentes ou de tipo inválido, identificadores repetidos, enums desconhecidos e datas sem UTC geram `TaskValidationError`. `data_conclusao < data_criacao` também gera `TaskValidationError`, conforme o cenário de erro da fase 2. Uma tarefa concluída com `data_conclusao < data_inicio` ou `data_inicio < data_criacao` é excluída dos cálculos, conforme RN04 da fase 1.

## Regras de cálculo

1. Apenas tarefas `concluida` com datas consistentes entram nas médias e na taxa de atraso. Pendentes e canceladas não entram nesses cálculos.
2. A duração é `data_conclusao - data_inicio`. O valor em minutos segue a fase 1; o valor em horas atende a fase 2.
3. Há atraso somente se `data_conclusao > prazo` (igualdade não é atraso).
4. A taxa de atraso é `tarefas concluídas válidas atrasadas / tarefas concluídas válidas * 100`.
5. Médias e percentuais são arredondados a duas casas decimais. As contagens são inteiros.
6. Os indicadores são calculados separadamente para `baixa`, `media` e `alta`, sempre presentes na saída.

## Saída

```python
{
    "total_tarefas": int,
    "total_concluidas": int,
    "total_pendentes": int,
    "quantidade_tarefas": int,
    "tempo_medio_conclusao_min": float,
    "tempo_medio_conclusao_horas": float,
    "taxa_atraso_percentual": float,
    "indicadores_por_prioridade": {
        "baixa": {
            "quantidade_tarefas": int,
            "tempo_medio_conclusao_min": float,
            "tempo_medio_conclusao_horas": float,
            "taxa_atraso_percentual": float,
        },
        "media": { ... },
        "alta": { ... },
    },
}
```

`total_concluidas` conta tarefas com esse status, inclusive as excluídas por inconsistência temporal; `quantidade_tarefas` conta apenas as concluídas válidas usadas nas métricas. `total_pendentes` conta as tarefas com status `pendente`. Tarefas canceladas entram apenas em `total_tarefas`.

## Ajustes da fase 2

O SDD da fase 1 especificava somente `quantidade_tarefas`, média em minutos e exceção quando não houvesse tarefa concluída válida. O enunciado da fase 2 pede também `total_tarefas`, `total_concluidas`, `total_pendentes`, média em horas (geral e por prioridade) e média `0.0` para lista vazia ou só pendentes. Para cumprir a entrega atual, esses campos foram adicionados e grupos sem tarefas concluídas válidas retornam duração média e taxa de atraso `0.0`. Nenhum `ZeroDivisionError` é exposto. Os campos originais em minutos continuam presentes para preservar a rastreabilidade da fase 1.

## Cenários de aceite

### Cenário 1 — sucesso

Seis tarefas: quatro concluídas válidas (durações de 60, 90, 150 e 60 minutos, distribuídas entre `baixa`, `media`, `alta`, `baixa`), uma pendente e uma cancelada. Somente a segunda tarefa concluída está atrasada. Resultado geral: `quantidade_tarefas=4`, `tempo_medio_conclusao_min=90.0`, `tempo_medio_conclusao_horas=1.5`, `taxa_atraso_percentual=25.0`, `total_tarefas=6`, `total_concluidas=4`, `total_pendentes=1`. Por prioridade: `baixa` tem 2 tarefas, 60 minutos/1 hora e 0% de atraso; `media` tem 1 tarefa, 90 minutos/1,5 hora e 100%; `alta` tem 1 tarefa, 150 minutos/2,5 horas e 0%.

### Cenário 2 — erro

Uma tarefa com `data_conclusao < data_criacao` deve lançar `TaskValidationError` com mensagem clara. Uma tarefa com conclusão antes do início não contribui para os cálculos.

### Casos de borda

Lista vazia, lista sem tarefas concluídas e prioridade sem tarefas válidas retornam médias e taxa `0.0` nas respectivas métricas, sem divisão por zero.

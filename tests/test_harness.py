"""Cenários de aceite da fase 1 e ajustes exigidos na fase 2."""

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402


def utc(day: int, hour: int, minute: int = 0) -> datetime:
    """Cria uma data UTC para setembro de 2026."""
    return datetime(2026, 9, day, hour, minute, tzinfo=timezone.utc)


def task(
    identifier: int,
    priority: str,
    status: str,
    created: datetime,
    started: datetime | None,
    finished: datetime | None,
    deadline: datetime,
) -> dict[str, object]:
    """Monta uma tarefa conforme o contrato público."""
    return {
        "id_tarefa": identifier,
        "prioridade": priority,
        "status": status,
        "data_criacao": created,
        "data_inicio": started,
        "data_conclusao": finished,
        "prazo": deadline,
    }


def test_scenario_1_success() -> None:
    """Confere contagens, médias e atraso geral e por prioridade."""
    tasks = [
        task(1, "baixa", "concluida", utc(1, 8), utc(1, 9), utc(1, 10), utc(1, 11)),
        task(
            2, "media", "concluida", utc(1, 8), utc(1, 9, 30),
            utc(1, 11), utc(1, 10, 30),
        ),
        task(
            3, "alta", "concluida", utc(1, 12), utc(1, 13),
            utc(1, 15, 30), utc(1, 16),
        ),
        task(4, "baixa", "concluida", utc(2, 7), utc(2, 8), utc(2, 9), utc(2, 9, 30)),
        task(5, "media", "pendente", utc(2, 9), utc(2, 10), None, utc(2, 12)),
        task(6, "alta", "cancelada", utc(2, 9), None, None, utc(2, 15)),
    ]

    result = analyze_tasks(tasks)

    assert result == {
        "total_tarefas": 6,
        "total_concluidas": 4,
        "total_pendentes": 1,
        "quantidade_tarefas": 4,
        "tempo_medio_conclusao_min": 90.0,
        "tempo_medio_conclusao_horas": 1.5,
        "taxa_atraso_percentual": 25.0,
        "indicadores_por_prioridade": {
            "baixa": {
                "quantidade_tarefas": 2,
                "tempo_medio_conclusao_min": 60.0,
                "tempo_medio_conclusao_horas": 1.0,
                "taxa_atraso_percentual": 0.0,
            },
            "media": {
                "quantidade_tarefas": 1,
                "tempo_medio_conclusao_min": 90.0,
                "tempo_medio_conclusao_horas": 1.5,
                "taxa_atraso_percentual": 100.0,
            },
            "alta": {
                "quantidade_tarefas": 1,
                "tempo_medio_conclusao_min": 150.0,
                "tempo_medio_conclusao_horas": 2.5,
                "taxa_atraso_percentual": 0.0,
            },
        },
    }
    assert isinstance(result["total_tarefas"], int)
    assert isinstance(result["tempo_medio_conclusao_horas"], float)


def test_scenario_2_completion_before_creation() -> None:
    """Rejeita a data inconsistente exigida na fase 2."""
    invalid = task(
        1, "baixa", "concluida", utc(3, 10), utc(3, 8), utc(3, 9), utc(3, 12)
    )

    with pytest.raises(TaskValidationError, match="data_conclusao.*data_criacao"):
        analyze_tasks([invalid])


def test_completion_before_start_is_excluded() -> None:
    """Preserva a regra RN04 do SDD da fase 1."""
    invalid = task(
        1, "alta", "concluida", utc(3, 7), utc(3, 10), utc(3, 9), utc(3, 12)
    )
    valid = task(
        2, "baixa", "concluida", utc(3, 7), utc(3, 8), utc(3, 9), utc(3, 9)
    )

    result = analyze_tasks([invalid, valid])

    assert result["total_concluidas"] == 2
    assert result["quantidade_tarefas"] == 1
    assert result["tempo_medio_conclusao_min"] == 60.0
    assert result["taxa_atraso_percentual"] == 0.0
    assert result["indicadores_por_prioridade"]["alta"]["quantidade_tarefas"] == 0


@pytest.mark.parametrize(
    ("tasks", "expected_total", "expected_pending"),
    [
        ([], 0, 0),
        ([task(1, "media", "pendente", utc(2, 9), None, None, utc(2, 12))], 1, 1),
        ([task(1, "alta", "cancelada", utc(2, 9), None, None, utc(2, 12))], 1, 0),
    ],
)
def test_no_valid_completed_tasks_returns_zero(
    tasks: list[dict[str, object]], expected_total: int, expected_pending: int
) -> None:
    """Evita divisão por zero para entradas sem conclusão calculável."""
    result = analyze_tasks(tasks)

    assert result["total_tarefas"] == expected_total
    assert result["total_pendentes"] == expected_pending
    assert result["quantidade_tarefas"] == 0
    assert result["tempo_medio_conclusao_min"] == 0.0
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0
    assert all(
        metrics["tempo_medio_conclusao_horas"] == 0.0
        for metrics in result["indicadores_por_prioridade"].values()
    )


def test_invalid_domain_is_rejected() -> None:
    """Impede cálculo sobre valores fora do contrato."""
    invalid = task(
        1, "urgente", "concluida", utc(1, 8), utc(1, 9), utc(1, 10), utc(1, 11)
    )

    with pytest.raises(TaskValidationError, match="prioridade"):
        analyze_tasks([invalid])


def test_average_and_delay_are_rounded() -> None:
    """Confere arredondamento e prazo estrito em tarefas válidas."""
    tasks = [
        task(1, "baixa", "concluida", utc(1, 8), utc(1, 9), utc(1, 9, 1), utc(1, 9, 1)),
        task(2, "baixa", "concluida", utc(1, 8), utc(1, 9), utc(1, 9, 2), utc(1, 9, 1)),
        task(3, "baixa", "concluida", utc(1, 8), utc(1, 9), utc(1, 9, 2), utc(1, 9, 1)),
    ]

    result = analyze_tasks(tasks)

    assert result["tempo_medio_conclusao_min"] == 1.67
    assert result["tempo_medio_conclusao_horas"] == 0.03
    assert result["taxa_atraso_percentual"] == 66.67

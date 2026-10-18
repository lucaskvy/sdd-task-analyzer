"""Calcula métricas de conclusão e atraso para tarefas em UTC."""

from datetime import datetime, timedelta


class TaskValidationError(ValueError):
    """Indica que uma tarefa não atende ao contrato de entrada."""


def _utc_datetime(value: object, field: str, required: bool) -> datetime | None:
    """Valida uma data UTC de entrada.

    Args:
        value: Valor recebido no campo.
        field: Nome do campo para a mensagem de erro.
        required: Indica se o campo é obrigatório.

    Returns:
        A data validada ou ``None`` para um campo opcional ausente.

    Raises:
        TaskValidationError: Se a data obrigatória faltar ou não estiver em UTC.
    """
    if value is None and not required:
        return None
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise TaskValidationError(f"{field} deve ser uma data e hora em UTC.")
    return value


def _metrics(records: list[tuple[str, float, bool]]) -> dict[str, int | float]:
    """Resume tarefas concluídas válidas de um grupo.

    Args:
        records: Prioridade, duração em minutos e indicador de atraso.

    Returns:
        Contagem, médias e taxa de atraso do grupo.
    """
    count = len(records)
    if count == 0:
        return {
            "quantidade_tarefas": 0,
            "tempo_medio_conclusao_min": 0.0,
            "tempo_medio_conclusao_horas": 0.0,
            "taxa_atraso_percentual": 0.0,
        }

    average_minutes = sum(duration for _, duration, _ in records) / count
    overdue = sum(is_late for _, _, is_late in records)
    return {
        "quantidade_tarefas": count,
        "tempo_medio_conclusao_min": round(average_minutes, 2),
        "tempo_medio_conclusao_horas": round(average_minutes / 60, 2),
        "taxa_atraso_percentual": round(overdue / count * 100, 2),
    }


def analyze_tasks(tasks: list[dict[str, object]]) -> dict[str, object]:
    """Analisa tarefas e devolve métricas gerais e por prioridade.

    Args:
        tasks: Lista de tarefas conforme ``specs/task_analyzer_spec.md``.

    Returns:
        Contagens, médias em minutos e horas, taxa de atraso e indicadores
        para as três prioridades. Grupos sem conclusão válida têm métricas
        numéricas iguais a zero.

    Raises:
        TaskValidationError: Se uma entrada não atender ao contrato.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("tasks deve ser uma lista de tarefas.")

    completed: list[tuple[str, float, bool]] = []
    identifiers: set[int] = set()
    completed_count = 0
    pending_count = 0

    for task in tasks:
        if not isinstance(task, dict):
            raise TaskValidationError("Cada tarefa deve ser um dicionário.")

        identifier = task.get("id_tarefa")
        if type(identifier) is not int or identifier <= 0:
            raise TaskValidationError("id_tarefa deve ser um inteiro maior que zero.")
        if identifier in identifiers:
            raise TaskValidationError(f"id_tarefa duplicado: {identifier}.")
        identifiers.add(identifier)

        priority = task.get("prioridade")
        if not isinstance(priority, str) or priority not in {"baixa", "media", "alta"}:
            raise TaskValidationError("prioridade deve ser baixa, media ou alta.")

        status = task.get("status")
        if not isinstance(status, str) or status not in {
            "concluida", "pendente", "cancelada"
        }:
            raise TaskValidationError(
                "status deve ser concluida, pendente ou cancelada."
            )

        created = _utc_datetime(task.get("data_criacao"), "data_criacao", True)
        started = _utc_datetime(task.get("data_inicio"), "data_inicio", False)
        finished = _utc_datetime(task.get("data_conclusao"), "data_conclusao", False)
        deadline = _utc_datetime(task.get("prazo"), "prazo", True)

        if created is None or deadline is None:
            raise TaskValidationError("data_criacao e prazo são obrigatórios.")
        if finished is not None and finished < created:
            raise TaskValidationError(
                "data_conclusao não pode ser anterior a data_criacao."
            )

        if status == "pendente":
            pending_count += 1
        if status != "concluida":
            continue

        completed_count += 1
        if started is None or finished is None:
            raise TaskValidationError(
                "Tarefa concluida exige data_inicio e data_conclusao."
            )
        if started < created or finished < started:
            continue

        duration_minutes = (finished - started).total_seconds() / 60
        completed.append((priority, duration_minutes, finished > deadline))

    result: dict[str, object] = {
        "total_tarefas": len(tasks),
        "total_concluidas": completed_count,
        "total_pendentes": pending_count,
        **_metrics(completed),
        "indicadores_por_prioridade": {
            priority: _metrics([row for row in completed if row[0] == priority])
            for priority in ("baixa", "media", "alta")
        },
    }
    return result

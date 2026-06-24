"""
Registra cada tentativa do ciclo TDD em workspace/run_log.jsonl.
Cada linha é um JSON independente (formato JSONL).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(__file__).parent / "workspace" / "run_log.jsonl"


def log_attempt(
    *,
    requisito: str,
    tentativa: int,
    codigo: str,
    pytest_passou: bool,
    motivo_falha: str | None,
    fase: str,
) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fase": fase,
        "tentativa": tentativa,
        "requisito": requisito,
        "codigo": codigo,
        "pytest_passou": pytest_passou,
        "motivo_falha": motivo_falha,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_validation(
    *,
    requisito: str,
    codigo_final: str,
    pytest_passou: bool,
    motivo_falha: str | None,
) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fase": "VALIDACAO",
        "requisito": requisito,
        "codigo_final": codigo_final,
        "pytest_passou": pytest_passou,
        "motivo_falha": motivo_falha,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

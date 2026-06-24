"""
Responsável por escrever os arquivos no workspace e rodar o pytest de
verdade — é essa execução real (não a opinião do modelo) que decide se
a fase RED ou GREEN foi concluída.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

WORKSPACE_DIR = Path(__file__).parent / "workspace"


@dataclass
class TestResult:
    passed: bool
    output: str


def write_file(filename: str, content: str) -> Path:
    WORKSPACE_DIR.mkdir(exist_ok=True)
    path = WORKSPACE_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


def run_pytest(test_filename: str) -> TestResult:
    """
    Executa pytest apenas no arquivo de teste indicado, dentro do
    workspace, e captura saída para decidir o próximo passo e também
    para servir de feedback ao Agente de Código em caso de falha.
    """
    result = subprocess.run(
        ["python", "-m", "pytest", test_filename, "-v"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    passed = result.returncode == 0
    output = result.stdout + "\n" + result.stderr
    return TestResult(passed=passed, output=output)

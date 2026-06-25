"""
Responsável por escrever os arquivos no workspace e rodar os testes de
verdade — é essa execução real (não a opinião do modelo) que decide se
a fase RED ou GREEN foi concluída.

Suporte a múltiplas linguagens via dispatcher. Cada linguagem define:
- arquivos de solução e teste
- como inicializar o workspace
- como executar os testes
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

WORKSPACE_DIR = Path(__file__).parent / "workspace"


@dataclass
class LanguageConfig:
    name: str
    solution_file: str
    test_file: str
    validation_file: str


LANGUAGES: dict[str, LanguageConfig] = {
    "python": LanguageConfig(
        name="python",
        solution_file="solution.py",
        test_file="test_solution.py",
        validation_file="test_validation.py",
    ),
    "flutter": LanguageConfig(
        name="flutter",
        solution_file="lib/solution.dart",
        test_file="test/solution_test.dart",
        validation_file="test/validation_test.dart",
    ),
}


@dataclass
class TestResult:
    passed: bool
    output: str


def _strip_markdown_fences(content: str) -> str:
    lines = content.splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def write_file(filename: str, content: str) -> Path:
    path = WORKSPACE_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_strip_markdown_fences(content), encoding="utf-8")
    return path


def setup_workspace(language: str) -> None:
    """Inicializa o workspace com a estrutura necessária para cada linguagem."""
    WORKSPACE_DIR.mkdir(exist_ok=True)
    if language == "flutter":
        _setup_flutter_workspace()


def _setup_flutter_workspace() -> None:
    import shutil
    if not shutil.which("flutter"):
        raise RuntimeError(
            "Flutter SDK não encontrado. Instale o SDK e adicione 'flutter' ao PATH.\n"
            "Consulte: https://docs.flutter.dev/get-started/install"
        )

    flutter_project = WORKSPACE_DIR / "flutter_project"
    if flutter_project.exists():
        return

    result = subprocess.run(
        ["flutter", "create", "--no-pub", "flutter_project"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Falha ao criar projeto Flutter:\n{result.stdout}\n{result.stderr}"
        )


def run_tests(test_filename: str, language: str) -> TestResult:
    if language == "python":
        return _run_python_tests(test_filename)
    elif language == "flutter":
        return _run_flutter_tests(test_filename)
    raise ValueError(f"Linguagem não suportada: {language}")


def _run_python_tests(test_filename: str) -> TestResult:
    result = subprocess.run(
        ["python3", "-m", "pytest", test_filename, "-v"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    passed = result.returncode == 0
    output = result.stdout + "\n" + result.stderr
    return TestResult(passed=passed, output=output)


def _run_flutter_tests(test_filename: str) -> TestResult:
    flutter_project = WORKSPACE_DIR / "flutter_project"
    result = subprocess.run(
        ["flutter", "test", test_filename],
        cwd=flutter_project,
        capture_output=True,
        text=True,
        timeout=120,
    )
    passed = result.returncode == 0
    output = result.stdout + "\n" + result.stderr
    return TestResult(passed=passed, output=output)

"""
Máquina de estados que executa o ciclo:

  Humano define requisito
      -> Agente de Testes (RED)        [aprovação humana]
      -> Agente de Código (GREEN)      [roda pytest de verdade]
      -> aprovação humana
      -> Agente de Validação (testes independentes)
      -> se falhar, volta para o Agente de Código com feedback

Cada transição só acontece se a etapa anterior foi aprovada (humano)
ou validada (pytest real) — o LLM nunca decide por si só que terminou.
"""

from enum import Enum, auto

from agents import CodeAgent, TestAgent, ValidationAgent
from cli import ask_approval, ask_export
from llm_client import LLMClient
from run_logger import log_attempt, log_validation
from test_runner import WORKSPACE_DIR, run_pytest, write_file

MAX_CODE_ATTEMPTS = 3
TEST_FILENAME = "test_solution.py"
VALIDATION_FILENAME = "test_validation.py"
SOLUTION_FILENAME = "solution.py"


def _extract_failure_summary(pytest_output: str, test_code: str) -> str:
    """Constrói feedback explícito combinando erros do pytest com os testes."""
    lines = pytest_output.splitlines()
    relevant = [l for l in lines if any(k in l for k in ("FAILED", "AssertionError", "assert", "Error", "raise", "E  ", ">>"))]
    errors = "\n".join(relevant[:40]) or pytest_output[:1000]
    return (
        "Sua implementação falhou nos testes. Leia os testes abaixo com atenção "
        "e observe os valores de entrada e saída esperados — eles são a fonte de "
        "verdade absoluta, independente do seu conhecimento do domínio.\n\n"
        f"Testes:\n{test_code}\n\n"
        f"Erros encontrados:\n{errors}"
    )


class Estado(Enum):
    AGUARDANDO_REQUISITO = auto()
    GERANDO_TESTE = auto()
    AGUARDANDO_APROVACAO_TESTE = auto()
    GERANDO_CODIGO = auto()
    EXECUTANDO_TESTE = auto()
    AGUARDANDO_APROVACAO_CODIGO = auto()
    VALIDACAO_FINAL = auto()
    CONCLUIDO = auto()
    FALHOU = auto()


class TDDOrchestrator:
    def __init__(self):
        client = LLMClient()
        self.test_agent = TestAgent(client)
        self.code_agent = CodeAgent(client)
        self.validation_agent = ValidationAgent(client)
        self.estado = Estado.AGUARDANDO_REQUISITO

    def run(self, requirement: str) -> Estado:
        self.estado = Estado.GERANDO_TESTE

        # --- Fase RED: gerar testes a partir do requisito ---
        test_code = self.test_agent.generate_tests(requirement)
        write_file(TEST_FILENAME, test_code)

        self.estado = Estado.AGUARDANDO_APROVACAO_TESTE
        decision = ask_approval("Testes gerados (fase RED)", test_code)
        if not decision.approved:
            print("Processo interrompido na aprovação dos testes.")
            self.estado = Estado.FALHOU
            return self.estado

        # --- Fase GREEN: implementar até passar, com retentativas ---
        self.estado = Estado.GERANDO_CODIGO
        feedback = None
        for attempt in range(1, MAX_CODE_ATTEMPTS + 1):
            implementation_code = self.code_agent.generate_implementation(
                test_code, feedback
            )
            write_file(SOLUTION_FILENAME, implementation_code)

            self.estado = Estado.EXECUTANDO_TESTE
            result = run_pytest(TEST_FILENAME)

            log_attempt(
                requisito=requirement,
                tentativa=attempt,
                codigo=implementation_code,
                pytest_passou=result.passed,
                motivo_falha=None if result.passed else result.output,
                fase="GREEN",
            )

            if result.passed:
                break

            print(f"Tentativa {attempt}/{MAX_CODE_ATTEMPTS} falhou nos testes.")
            feedback = _extract_failure_summary(result.output, test_code)
        else:
            print("Número máximo de tentativas atingido sem sucesso.")
            self.estado = Estado.FALHOU
            return self.estado

        self.estado = Estado.AGUARDANDO_APROVACAO_CODIGO
        decision = ask_approval("Implementação gerada (fase GREEN)", implementation_code)
        if not decision.approved:
            print("Processo interrompido na aprovação do código.")
            self.estado = Estado.FALHOU
            return self.estado

        # --- Validação final: testes independentes, sem ver os testes originais ---
        self.estado = Estado.VALIDACAO_FINAL
        validation_test_code = self.validation_agent.generate_validation_tests(
            requirement, implementation_code
        )
        write_file(VALIDATION_FILENAME, validation_test_code)
        validation_result = run_pytest(VALIDATION_FILENAME)

        log_validation(
            requisito=requirement,
            codigo_final=implementation_code,
            pytest_passou=validation_result.passed,
            motivo_falha=None if validation_result.passed else validation_result.output,
        )

        if validation_result.passed:
            print("Validação independente aprovada. Processo concluído.")
            self.estado = Estado.CONCLUIDO
            ask_export(WORKSPACE_DIR, SOLUTION_FILENAME, TEST_FILENAME)
        else:
            print("Validação independente reprovou a implementação:")
            print(validation_result.output)
            self.estado = Estado.FALHOU

        return self.estado

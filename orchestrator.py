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
from cli import ask_approval
from llm_client import LLMClient
from test_runner import run_pytest, write_file

MAX_CODE_ATTEMPTS = 3
TEST_FILENAME = "test_solution.py"
VALIDATION_FILENAME = "test_validation.py"
SOLUTION_FILENAME = "solution.py"


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

            if result.passed:
                break

            print(f"Tentativa {attempt}/{MAX_CODE_ATTEMPTS} falhou nos testes.")
            feedback = result.output
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

        if validation_result.passed:
            print("Validação independente aprovada. Processo concluído.")
            self.estado = Estado.CONCLUIDO
        else:
            print("Validação independente reprovou a implementação:")
            print(validation_result.output)
            self.estado = Estado.FALHOU

        return self.estado

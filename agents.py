"""
Cada agente é uma combinação de: prompt de sistema fixo + uma forma
específica de montar a mensagem do usuário a partir do estado atual
do processo. Isso mantém os três papéis isolados — importante para que
o Agente de Validação não "veja" o que os outros dois fizeram além do
que é explicitamente passado para ele.
"""

from pathlib import Path

from llm_client import LLMClient

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


class TestAgent:
    """Fase RED: gera testes a partir do requisito em linguagem natural."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.system_prompt = _load_prompt("test_agent_prompt.txt")

    def generate_tests(self, requirement: str) -> str:
        return self.llm_client.chat(self.system_prompt, requirement)


class CodeAgent:
    """Fase GREEN: implementa código até os testes passarem."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.system_prompt = _load_prompt("code_agent_prompt.txt")

    def generate_implementation(self, test_code: str, feedback: str | None = None) -> str:
        message = f"Testes a satisfazer:\n\n{test_code}"
        if feedback:
            message += f"\n\nFeedback da tentativa anterior:\n{feedback}"
        return self.llm_client.chat(self.system_prompt, message, temperature=0.1)


class ValidationAgent:
    """
    Fase de validação final: gera um conjunto de testes NOVO e
    independente, vendo apenas o requisito original e o código final —
    nunca os testes que guiaram o desenvolvimento.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.system_prompt = _load_prompt("validation_agent_prompt.txt")

    def generate_validation_tests(self, requirement: str, implementation_code: str) -> str:
        message = (
            f"Requisito original:\n{requirement}\n\n"
            f"Implementação final a validar:\n{implementation_code}"
        )
        return self.llm_client.chat(self.system_prompt, message)

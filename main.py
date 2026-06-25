"""
Uso:
    python3 main.py

Pré-requisito: ter o RamaLama servindo um modelo localmente, ex:
    ramalama serve gemma3:4b

Isso expõe o endpoint que llm_client.py espera em http://localhost:8080/v1
"""

from orchestrator import TDDOrchestrator
from test_runner import LANGUAGES


def main():
    print("=== Orquestrador de TDD com agentes de IA ===\n")

    linguagens = list(LANGUAGES.keys())
    while True:
        language = input(f"Linguagem {linguagens} (padrão: python): ").strip().lower() or "python"
        if language in LANGUAGES:
            break
        print(f"  Opções disponíveis: {linguagens}")

    requirement = input("\nDescreva o requisito da função a implementar:\n> ").strip()

    orchestrator = TDDOrchestrator(language=language)
    estado_final = orchestrator.run(requirement)

    print(f"\nEstado final: {estado_final.name}")


if __name__ == "__main__":
    main()

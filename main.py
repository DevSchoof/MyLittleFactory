"""
Uso:
    python main.py

Pré-requisito: ter o RamaLama servindo um modelo localmente, ex:
    ramalama serve gemma3:4b

Isso expõe o endpoint que llm_client.py espera em http://localhost:8080/v1
"""

from orchestrator import TDDOrchestrator


def main():
    print("=== Orquestrador de TDD com agentes de IA ===\n")
    requirement = input("Descreva o requisito da função a implementar:\n> ").strip()

    orchestrator = TDDOrchestrator()
    estado_final = orchestrator.run(requirement)

    print(f"\nEstado final: {estado_final.name}")


if __name__ == "__main__":
    main()

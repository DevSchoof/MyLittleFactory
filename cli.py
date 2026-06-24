"""
Checkpoint de aprovação humana. Em produção isso poderia virar uma
tela web mostrando diff, mas para o MVP uma CLI já cumpre o papel
essencial: nada avança sem decisão explícita sua.
"""

from dataclasses import dataclass


@dataclass
class ApprovalDecision:
    approved: bool
    comment: str = ""


def ask_approval(title: str, content: str) -> ApprovalDecision:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(content)
    print("=" * 60)

    answer = input("Aprovar? [s/n]: ").strip().lower()
    if answer == "s":
        return ApprovalDecision(approved=True)

    comment = input("Motivo da rejeição (vira feedback para o agente): ").strip()
    return ApprovalDecision(approved=False, comment=comment)

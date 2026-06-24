"""
Checkpoint de aprovação humana. Em produção isso poderia virar uma
tela web mostrando diff, mas para o MVP uma CLI já cumpre o papel
essencial: nada avança sem decisão explícita sua.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path


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

    while True:
        answer = input("Aprovar? [s/n]: ").strip().lower()
        if answer == "s":
            return ApprovalDecision(approved=True)
        if answer == "n":
            break
        print("  Digite 's' para aprovar ou 'n' para rejeitar.")

    comment = input("Motivo da rejeição (vira feedback para o agente): ").strip()
    return ApprovalDecision(approved=False, comment=comment)


def ask_export(workspace_dir: Path, solution_filename: str, test_filename: str) -> None:
    answer = input("\nDeseja exportar os arquivos gerados? [s/n]: ").strip().lower()
    if answer != "s":
        return

    dest = input("Caminho de destino (ex: ~/meu_projeto): ").strip()
    dest_path = Path(dest).expanduser().resolve()
    dest_path.mkdir(parents=True, exist_ok=True)

    for filename in [solution_filename, test_filename]:
        src = workspace_dir / filename
        if src.exists():
            shutil.copy(src, dest_path / filename)
            print(f"  {filename} -> {dest_path / filename}")

    print(f"Arquivos exportados para {dest_path}")

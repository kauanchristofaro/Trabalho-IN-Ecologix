"""Adiciona periodo_id aos CSVs mensais usados pelo Power BI."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

MESES = {
    "Jan": 1,
    "Fev": 2,
    "Mar": 3,
    "Abr": 4,
    "Mai": 5,
    "Jun": 6,
    "Jul": 7,
    "Ago": 8,
    "Set": 9,
    "Out": 10,
    "Nov": 11,
    "Dez": 12,
}

MONTHLY_FILES = [
    "entregas_mensal.csv",
    "entregas_regional.csv",
    "financeiro_mensal.csv",
    "sustentabilidade_mensal.csv",
    "clientes_mensal.csv",
    "comparativo_empresas_mensal.csv",
    "roi_investimento_mensal.csv",
]


def periodo_id(mes: str, ano: str | int) -> int:
    return int(ano) * 100 + MESES[mes]


def enrich_monthly_csv(path: Path) -> None:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return
    if "periodo_id" in rows[0]:
        print(f"OK: {path.name} ja possui periodo_id")
        return

    fieldnames = ["periodo_id", *rows[0].keys()]
    for row in rows:
        pid = periodo_id(row["mes"], row["ano"])
        row["periodo_id"] = str(pid)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Atualizado: {path.name}")


def main() -> None:
    for name in MONTHLY_FILES:
        enrich_monthly_csv(DATA / name)


if __name__ == "__main__":
    main()

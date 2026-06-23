"""Corrige conexoes CSV do EcoLogix_Dashboard_v2.pbit."""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from powerbi_queries import TABLES, build_m_lines

ROOT = Path(__file__).resolve().parents[1]
PBIT = ROOT / "EcoLogix_Dashboard_v2.pbit"
DATA_DIR = ROOT / "data"


def load_schema(pbit_path: Path) -> dict:
    with zipfile.ZipFile(pbit_path) as archive:
        return json.loads(archive.read("DataModelSchema").decode("utf-16-le"))


def save_schema(pbit_path: Path, schema: dict) -> None:
    temp_path = pbit_path.with_suffix(".pbit.tmp")
    with zipfile.ZipFile(pbit_path, "r") as source, zipfile.ZipFile(temp_path, "w") as target:
        schema_bytes = json.dumps(schema, ensure_ascii=False, indent=2).encode("utf-16-le")
        for item in source.infolist():
            data = schema_bytes if item.filename == "DataModelSchema" else source.read(item.filename)
            target.writestr(item, data)
    temp_path.replace(pbit_path)


def fix_connections(pbit_path: Path = PBIT, data_dir: Path = DATA_DIR) -> None:
    from preparar_csv import main as preparar_csv

    preparar_csv()
    data_folder = str(data_dir.resolve()).replace("/", "\\")
    schema = load_schema(pbit_path)
    model = schema["model"]

    model["expressions"] = [
        {
            "name": "DataFolderPath",
            "kind": "m",
            "expression": [
                f'"{data_folder}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true, '
                f'Description="Pasta com os arquivos CSV do EcoLogix"]'
            ],
        }
    ]

    for table in model["tables"]:
        name = table["name"]
        if name not in TABLES or not table.get("partitions"):
            continue
        partition = table["partitions"][0]
        source = partition.setdefault("source", {})
        source["type"] = "m"
        source["expression"] = build_m_lines(name, data_dir, use_parameter=True)

    save_schema(pbit_path, schema)
    print(f"Template corrigido: {pbit_path}")
    print(f"DataFolderPath: {data_folder}")


def verify(pbit_path: Path = PBIT) -> None:
    schema = load_schema(pbit_path)
    errors = []
    for table in schema["model"]["tables"]:
        name = table["name"]
        if name not in TABLES:
            continue
        expr = "\n".join(table["partitions"][0]["source"].get("expression", []))
        if "#table(" in expr:
            errors.append(f"{name} ainda usa tabela inline")
        if "DataFolderPath" not in expr:
            errors.append(f"{name} sem DataFolderPath")
        if TABLES[name]["periodo_id"] and "WithPeriodo" not in expr:
            errors.append(f"{name} sem calculo de periodo_id")
    if errors:
        for error in errors:
            print(f"ERRO: {error}")
        raise SystemExit(1)
    print("Verificacao concluida.")


if __name__ == "__main__":
    backup = PBIT.with_suffix(".pbit.bak")
    if PBIT.exists() and not backup.exists():
        shutil.copy2(PBIT, backup)
    fix_connections()
    verify()

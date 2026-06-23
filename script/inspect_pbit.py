"""Inspect Power BI template connections."""
import json
import sys
import zipfile
from pathlib import Path


def fmt_expr(expr):
    if isinstance(expr, list):
        return "".join(expr)
    return str(expr or "")


def inspect_pbit(pbit_path: Path) -> None:
    with zipfile.ZipFile(pbit_path) as zf:
        schema_bytes = zf.read("DataModelSchema")

    schema = json.loads(schema_bytes.decode("utf-16-le"))
    model = schema["model"]

    print(f"File: {pbit_path.name}")
    print(f"Tables: {len(model.get('tables', []))}")
    print()

    print("=== TABLE PARTITIONS ===")
    for table in model.get("tables", []):
        name = table.get("name")
        for partition in table.get("partitions", []):
            source = partition.get("source", {})
            expr = fmt_expr(source.get("expression"))
            print(f"--- {name} (mode={partition.get('mode')}, type={source.get('type')}) ---")
            print(expr)
            print()

    print("=== EXPRESSIONS ===")
    for expr_def in model.get("expressions", []):
        print(f"--- {expr_def.get('name')} ---")
        print(fmt_expr(expr_def.get("expression")))
        print()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "EcoLogix_Dashboard_v2.pbit"
    inspect_pbit(target)

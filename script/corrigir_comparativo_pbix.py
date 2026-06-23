"""Atualiza apenas consultas M do .pbix (sem alterar tipos de coluna no metadata)."""
from __future__ import annotations

import shutil
import sqlite3
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PBIX = ROOT / "EcoLogix_Dashboard (1) (1).pbix"
DATA_DIR = ROOT / "data"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from powerbi_queries import TABLES, build_m_query  # noqa: E402
from preparar_csv import main as preparar_csv  # noqa: E402


def patch_m_queries(conn: sqlite3.Connection, data_dir: Path) -> int:
    updated = 0
    for table_name in TABLES:
        m_code = build_m_query(table_name, data_dir, use_parameter=False)
        row = conn.execute(
            "SELECT p.ID FROM [Partition] p "
            "JOIN [Table] t ON p.TableID = t.ID "
            "WHERE t.Name = ? AND p.QueryDefinition IS NOT NULL",
            (table_name,),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE [Partition] SET QueryDefinition = ? WHERE ID = ?",
                (m_code, row[0]),
            )
            updated += 1
    return updated


def fix_pbix(pbix_path: Path, data_dir: Path) -> None:
    from pbix_mcp.formats.abf_rebuild import rebuild_abf_with_modified_sqlite
    from pbix_mcp.formats.datamodel_roundtrip import compress_datamodel, decompress_datamodel

    preparar_csv()

    with zipfile.ZipFile(pbix_path, "r") as archive:
        abf = decompress_datamodel(archive.read("DataModel"))

    def modifier(conn: sqlite3.Connection) -> None:
        count = patch_m_queries(conn, data_dir)
        conn.commit()
        print(f"Consultas M atualizadas: {count}")

    new_abf = rebuild_abf_with_modified_sqlite(abf, modifier)
    new_datamodel = compress_datamodel(new_abf)

    temp_path = pbix_path.with_suffix(".pbix.tmp")
    with zipfile.ZipFile(pbix_path, "r") as source, zipfile.ZipFile(temp_path, "w") as target:
        for item in source.infolist():
            data = new_datamodel if item.filename == "DataModel" else source.read(item.filename)
            target.writestr(item, data)
    temp_path.replace(pbix_path)
    print(f"PBIX corrigido: {pbix_path}")


def main() -> None:
    pbix_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PBIX
    if not pbix_path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {pbix_path}")
    fix_pbix(pbix_path, DATA_DIR)


if __name__ == "__main__":
    main()

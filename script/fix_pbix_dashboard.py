"""Corrige conexoes e consultas M do EcoLogix_Dashboard.pbix."""
from __future__ import annotations

import shutil
import sqlite3
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBIX = ROOT / "EcoLogix_Dashboard.pbix"
DATA_DIR = ROOT / "data"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from powerbi_queries import TABLES, build_m_query  # noqa: E402
from preparar_csv import main as preparar_csv  # noqa: E402


def patch_metadata(conn: sqlite3.Connection, data_dir: Path) -> None:
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
                "UPDATE [Partition] SET QueryDefinition = ?, ModifiedTime = datetime('now') WHERE ID = ?",
                (m_code, row[0]),
            )


def fix_pbix(pbix_path: Path = PBIX, data_dir: Path = DATA_DIR) -> None:
    import sqlite3
    import tempfile
    import os

    from pbix_mcp.formats.abf_rebuild import read_metadata_sqlite, rebuild_abf_with_replacement
    from pbix_mcp.formats.datamodel_roundtrip import compress_datamodel, decompress_datamodel

    preparar_csv()

    backup = pbix_path.with_suffix(".pbix.bak")
    if not backup.exists():
        shutil.copy2(pbix_path, backup)

    with zipfile.ZipFile(pbix_path, "r") as archive:
        abf = decompress_datamodel(archive.read("DataModel"))

    sqlite_bytes = read_metadata_sqlite(abf)
    fd, tmp_path = tempfile.mkstemp(suffix=".sqlitedb")
    try:
        os.write(fd, sqlite_bytes)
        os.close(fd)
        conn = sqlite3.connect(tmp_path)
        try:
            patch_metadata(conn, data_dir)
            conn.commit()
        finally:
            conn.close()
        with open(tmp_path, "rb") as handle:
            new_sqlite_bytes = handle.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    new_abf = rebuild_abf_with_replacement(abf, {"metadata.sqlitedb": new_sqlite_bytes})
    new_datamodel = compress_datamodel(new_abf)

    temp_path = pbix_path.with_suffix(".pbix.tmp")
    with zipfile.ZipFile(pbix_path, "r") as source, zipfile.ZipFile(temp_path, "w") as target:
        for item in source.infolist():
            data = new_datamodel if item.filename == "DataModel" else source.read(item.filename)
            target.writestr(item, data)
    temp_path.replace(pbix_path)

    print(f"PBIX corrigido: {pbix_path}")
    print(f"Pasta de dados: {data_dir.resolve()}")
    print(f"Backup: {backup}")


def verify(pbix_path: Path = PBIX) -> None:
    from pbix_mcp.formats.model_reader import ModelReader

    reader = ModelReader(str(pbix_path))
    errors = []
    data_folder = str(DATA_DIR.resolve()).lower()
    for query in reader.power_query:
        name = query["TableName"]
        expr = query["Expression"] or ""
        if name not in TABLES:
            continue
        if "#table(" in expr:
            errors.append(f"{name} ainda usa tabela inline")
        if "ecologix_modulo3" in expr.lower():
            errors.append(f"{name} ainda usa caminho antigo")
        if TABLES[name]["periodo_id"] and "WithPeriodo" not in expr:
            errors.append(f"{name} sem calculo de periodo_id")
        if "data\\" not in expr.lower() and "data/" not in expr.lower():
            errors.append(f"{name} sem caminho para pasta data")
    if errors:
        for error in errors:
            print(f"ERRO: {error}")
        raise SystemExit(1)
    print("Verificacao concluida.")


if __name__ == "__main__":
    fix_pbix()
    verify()

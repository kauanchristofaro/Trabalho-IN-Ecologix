"""Restaura .pbix do backup e aplica apenas correcoes seguras (consultas M + medidas)."""
from __future__ import annotations

import datetime
import shutil
import sqlite3
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PBIX = ROOT / "EcoLogix_Dashboard (1) (1).pbix"
DEFAULT_BACKUP = DEFAULT_PBIX.with_suffix(".pbix.bak")
DATA_DIR = ROOT / "data"
TABLE_NAME = "ComparativoEmpresas"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from powerbi_queries import TABLES, build_m_query  # noqa: E402
from preparar_csv import main as preparar_csv  # noqa: E402

# Medidas com DAX simples — funcionam apos Atualizar os dados no Power BI.
NEW_MEASURES = [
    (
        "Receita Total LogiTrans",
        'CALCULATE(SUM(ComparativoEmpresas[receita_total_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
    (
        "CO2 Total LogiTrans",
        'CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
    (
        "CO2 por Entrega LogiTrans",
        'CALCULATE(AVERAGE(ComparativoEmpresas[co2_por_entrega_g]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
    (
        "Custo Medio Entrega LogiTrans",
        'CALCULATE(AVERAGE(ComparativoEmpresas[custo_medio_entrega_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
    (
        "Margem Lucro Entrega LogiTrans",
        'CALCULATE(AVERAGE(ComparativoEmpresas[margem_lucro_entrega_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
    (
        "Frota Combustao Media LogiTrans",
        'CALCULATE(AVERAGE(ComparativoEmpresas[frota_combustao_pct]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
    (
        "Margem Operacional Media LogiTrans",
        'CALCULATE(AVERAGE(ComparativoEmpresas[margem_operacional_pct]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
]


def _filetime_now() -> int:
    epoch = datetime.datetime(1601, 1, 1)
    return int((datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - epoch).total_seconds() * 10_000_000)


def _next_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT Value FROM DBPROPERTIES WHERE Name = 'MAXID'").fetchone()
    new_id = int(row[0]) + 1 if row else 1
    conn.execute("UPDATE DBPROPERTIES SET Value = ? WHERE Name = 'MAXID'", (str(new_id),))
    return new_id


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


def add_logitrans_measures(conn: sqlite3.Connection) -> list[str]:
    row = conn.execute("SELECT ID FROM [Table] WHERE Name = ?", (TABLE_NAME,)).fetchone()
    if not row:
        raise RuntimeError(f"Tabela {TABLE_NAME} nao encontrada.")
    table_id = row[0]
    existing = {
        name
        for (name,) in conn.execute(
            "SELECT Name FROM [Measure] WHERE TableID = ?", (table_id,)
        ).fetchall()
    }
    added: list[str] = []
    timestamp = _filetime_now()
    for name, expression in NEW_MEASURES:
        if name in existing:
            conn.execute(
                "UPDATE [Measure] SET Expression = ? WHERE Name = ? AND TableID = ?",
                (expression, name, table_id),
            )
            print(f"Medida atualizada: {name}")
            continue
        measure_id = _next_id(conn)
        conn.execute(
            """INSERT INTO [Measure] (
                ID, TableID, Name, Description, DataType,
                Expression, FormatString, IsHidden, State,
                ModifiedTime, StructureModifiedTime,
                KPIID, IsSimpleMeasure, ErrorMessage, DisplayFolder,
                DetailRowsDefinitionID, DataCategory,
                FormatStringDefinitionID, LineageTag, SourceLineageTag
            ) VALUES (
                ?, ?, ?, NULL, 6,
                ?, NULL, 0, 1,
                ?, ?,
                0, 0, NULL, NULL,
                0, NULL,
                0, ?, NULL
            )""",
            (measure_id, table_id, name, expression, timestamp, timestamp, str(uuid.uuid4())),
        )
        added.append(name)
    return added


def restore_and_fix(
    pbix_path: Path,
    backup_path: Path,
    data_dir: Path,
) -> None:
    from pbix_mcp.formats.abf_rebuild import rebuild_abf_with_modified_sqlite
    from pbix_mcp.formats.datamodel_roundtrip import compress_datamodel, decompress_datamodel

    preparar_csv()

    if not backup_path.exists():
        raise SystemExit(f"Backup nao encontrado: {backup_path}")

    shutil.copy2(backup_path, pbix_path)
    print(f"Restaurado de: {backup_path}")

    with zipfile.ZipFile(pbix_path, "r") as archive:
        abf = decompress_datamodel(archive.read("DataModel"))

    stats: dict[str, object] = {}

    def modifier(conn: sqlite3.Connection) -> None:
        stats["queries"] = patch_m_queries(conn, data_dir)
        stats["measures"] = add_logitrans_measures(conn)
        conn.commit()

    new_abf = rebuild_abf_with_modified_sqlite(abf, modifier)
    new_datamodel = compress_datamodel(new_abf)

    temp_path = pbix_path.with_suffix(".pbix.tmp")
    with zipfile.ZipFile(pbix_path, "r") as source, zipfile.ZipFile(temp_path, "w") as target:
        for item in source.infolist():
            data = new_datamodel if item.filename == "DataModel" else source.read(item.filename)
            target.writestr(item, data)
    temp_path.replace(pbix_path)

    print(f"PBIX restaurado e corrigido: {pbix_path}")
    print(f"Consultas M atualizadas: {stats.get('queries', 0)}")
    added = stats.get("measures", [])
    if added:
        print("Medidas adicionadas:")
        for name in added:
            print(f"  - {name}")
    print()
    print("IMPORTANTE: Abra o arquivo e clique em ATUALIZAR antes de usar as medidas.")


def main() -> None:
    pbix_path = DEFAULT_PBIX
    backup_path = DEFAULT_BACKUP
    args = sys.argv[1:]
    if args:
        pbix_path = Path(args[0])
        backup_path = Path(args[1]) if len(args) > 1 else pbix_path.with_suffix(".pbix.bak")
    restore_and_fix(pbix_path, backup_path, DATA_DIR)


if __name__ == "__main__":
    main()

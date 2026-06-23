"""Adiciona medidas DAX LogiTrans ao arquivo .pbix (metodo seguro via splice)."""
from __future__ import annotations

import datetime
import os
import shutil
import sqlite3
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PBIX = ROOT / "EcoLogix_Dashboard (1) (1).pbix"
TABLE_NAME = "ComparativoEmpresas"

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
    (
        "Custo Total Logitrans",
        'CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") + CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    ),
    (
        "CO2 Emitido por Real Logitrans",
        'DIVIDE(CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "LogiTrans Express") * 1000, CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") + CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express"))',
    ),
    (
        "CO2 Evitado por Real EcoLogix",
        'VAR InvestimentoEcoLogix = 3750000 VAR CO2FrotaKg = (CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")) * 1000 VAR Meses = CALCULATE(DISTINCTCOUNT(ComparativoEmpresas[periodo_id]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") VAR CO2SolarKg = Meses * 435.6 RETURN DIVIDE(CO2FrotaKg + CO2SolarKg, InvestimentoEcoLogix)',
    ),
    (
        "Economia Total por Real EcoLogix",
        'VAR InvestimentoEcoLogix = 3750000 VAR EconomiaFrota = CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") + CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") - CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") VAR Meses = CALCULATE(DISTINCTCOUNT(ComparativoEmpresas[periodo_id]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") VAR EconomiaSolar = Meses * 3431 RETURN DIVIDE(EconomiaFrota + EconomiaSolar, InvestimentoEcoLogix)',
    ),
]


def _filetime_now() -> int:
    epoch = datetime.datetime(1601, 1, 1)
    now = datetime.datetime.utcnow()
    return int((now - epoch).total_seconds() * 10_000_000)


def _next_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT Value FROM DBPROPERTIES WHERE Name = 'MAXID'").fetchone()
    new_id = int(row[0]) + 1 if row else 1
    conn.execute("UPDATE DBPROPERTIES SET Value = ? WHERE Name = 'MAXID'", (str(new_id),))
    return new_id


def patch_measures(conn: sqlite3.Connection) -> list[str]:
    row = conn.execute("SELECT ID FROM [Table] WHERE Name = ?", (TABLE_NAME,)).fetchone()
    if not row:
        raise RuntimeError(f"Tabela {TABLE_NAME} nao encontrada no modelo.")
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
            print(f"Ja existe: {name}")
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


def patch_pbix(pbix_path: Path, restore_backup: bool = False) -> None:
    from pbix_mcp.formats.abf_rebuild import rebuild_abf_with_modified_sqlite
    from pbix_mcp.formats.datamodel_roundtrip import compress_datamodel, decompress_datamodel

    backup = pbix_path.with_suffix(".pbix.bak")
    if restore_backup:
        if not backup.exists():
            raise SystemExit(f"Backup nao encontrado: {backup}")
        shutil.copy2(backup, pbix_path)
        print(f"Restaurado de: {backup}")
    elif not backup.exists():
        shutil.copy2(pbix_path, backup)
        print(f"Backup criado: {backup}")

    with zipfile.ZipFile(pbix_path, "r") as archive:
        abf = decompress_datamodel(archive.read("DataModel"))

    added_holder: list[str] = []

    def modifier(conn: sqlite3.Connection) -> None:
        added_holder.extend(patch_measures(conn))
        conn.commit()

    new_abf = rebuild_abf_with_modified_sqlite(abf, modifier)
    new_datamodel = compress_datamodel(new_abf)

    temp_path = pbix_path.with_suffix(".pbix.tmp")
    with zipfile.ZipFile(pbix_path, "r") as source, zipfile.ZipFile(temp_path, "w") as target:
        for item in source.infolist():
            data = new_datamodel if item.filename == "DataModel" else source.read(item.filename)
            target.writestr(item, data)
    temp_path.replace(pbix_path)

    print(f"PBIX atualizado: {pbix_path}")
    if added_holder:
        print("Medidas adicionadas:")
        for name in added_holder:
            print(f"  - {name}")
    else:
        print("Nenhuma medida nova (todas ja existiam).")


def main() -> None:
    pbix_path = DEFAULT_PBIX
    restore = False
    args = sys.argv[1:]
    if args and args[0] == "--restore":
        restore = True
        args = args[1:]
    if args:
        pbix_path = Path(args[0])
    if not pbix_path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {pbix_path}")
    patch_pbix(pbix_path, restore_backup=restore)


if __name__ == "__main__":
    main()

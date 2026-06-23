"""Adiciona medidas do simulador de investimento ao .pbix."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PBIX = ROOT / "EcoLogix_Dashboard (1) (1).pbix"
TABLE_NAME = "ComparativoEmpresas"

# Nome do parametro What-if criado manualmente no Power BI (Modelagem > Novo parametro).
PARAMETRO_WHATIF = "Input Investimento Reais"

NEW_MEASURES = [
    (
        "Investimento Simulado (R$)",
        "IF(HASONEVALUE('Input Investimento Reais'[Input Investimento Reais]), SELECTEDVALUE('Input Investimento Reais'[Input Investimento Reais]), MIN('Input Investimento Reais'[Input Investimento Reais]))",
    ),
    (
        "CO2 Evitado Simulado (kg)",
        "[Investimento Simulado (R$)] * [CO2 Evitado por Real EcoLogix]",
    ),
    (
        "Economia Simulada (R$)",
        "[Investimento Simulado (R$)] * [Economia Total por Real EcoLogix]",
    ),
    (
        "CO2 Evitado Simulado (t)",
        "[CO2 Evitado Simulado (kg)] / 1000",
    ),
    (
        "Despesas Estimadas EcoLogix (R$)",
        "[Investimento Simulado (R$)] * DIVIDE(242918, 3750000)",
    ),
    (
        "Despesas Estimadas LogiTrans (R$)",
        "[Investimento Simulado (R$)] * DIVIDE(724544, 3750000)",
    ),
    (
        "Diferenca Despesas LogiTrans vs EcoLogix (R$)",
        "[Despesas Estimadas LogiTrans (R$)] - [Despesas Estimadas EcoLogix (R$)]",
    ),
    (
        "Carbono Emitido EcoLogix (kg)",
        "[Investimento Simulado (R$)] * DIVIDE(9.44 * 1000, 3750000)",
    ),
    (
        "Carbono Emitido LogiTrans (kg)",
        "[Investimento Simulado (R$)] * DIVIDE(115.04 * 1000, 3750000)",
    ),
    (
        "Diferenca Carbono LogiTrans vs EcoLogix (kg)",
        "[Carbono Emitido LogiTrans (kg)] - [Carbono Emitido EcoLogix (kg)]",
    ),
]


def main() -> None:
    pbix_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PBIX
    if not pbix_path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {pbix_path}")

    from adicionar_medidas_logitrans import patch_pbix, patch_measures
    import sqlite3
    from pbix_mcp.formats.abf_rebuild import rebuild_abf_with_modified_sqlite
    from pbix_mcp.formats.datamodel_roundtrip import compress_datamodel, decompress_datamodel
    import datetime
    import shutil
    import zipfile

    backup = pbix_path.with_suffix(".pbix.bak")
    if not backup.exists():
        shutil.copy2(pbix_path, backup)
        print(f"Backup criado: {backup}")

    with zipfile.ZipFile(pbix_path, "r") as archive:
        abf = decompress_datamodel(archive.read("DataModel"))

    added_holder: list[str] = []

    def modifier(conn: sqlite3.Connection) -> None:
        added_holder.extend(patch_measures(conn))
        conn.commit()

    # Reuse patch_measures from sibling module by temporarily extending NEW_MEASURES
    import adicionar_medidas_logitrans as medidas_mod

    original = medidas_mod.NEW_MEASURES
    medidas_mod.NEW_MEASURES = original + NEW_MEASURES
    try:
        new_abf = rebuild_abf_with_modified_sqlite(abf, modifier)
    finally:
        medidas_mod.NEW_MEASURES = original

    new_datamodel = compress_datamodel(new_abf)
    temp_path = pbix_path.with_suffix(".pbix.tmp")
    with zipfile.ZipFile(pbix_path, "r") as source, zipfile.ZipFile(temp_path, "w") as target:
        for item in source.infolist():
            data = new_datamodel if item.filename == "DataModel" else source.read(item.filename)
            target.writestr(item, data)
    temp_path.replace(pbix_path)

    print(f"PBIX atualizado: {pbix_path}")
    if added_holder:
        print("Medidas do simulador adicionadas:")
        for name in added_holder:
            print(f"  - {name}")
    else:
        print("Medidas ja existiam ou nenhuma foi adicionada.")

    print()
    print_setup_instructions()


def print_setup_instructions() -> None:
    print("=" * 60)
    print("CONFIGURACAO NO POWER BI DESKTOP (obrigatoria 1x)")
    print("=" * 60)
    print()
    print("1. Modelagem > Novo parametro")
    print(f"   Nome: {PARAMETRO_WHATIF}")
    print("   Tipo: Numero decimal")
    print("   Minimo: 0 | Maximo: 5000000 | Incremento: 100")
    print("   Marque: Adicionar segmentacao a esta pagina")
    print()
    print("2. Na segmentacao (slicer), ative 'Opcoes' >")
    print("   Estilo > Entre (ou Valor unico) e digite o valor desejado.")
    print("   O campo aceita digitacao direta do valor em reais.")
    print()
    print("3. Insira 3 cards na pagina do simulador:")
    print(f"   - [{PARAMETRO_WHATIF} Value]  (valor digitado)")
    print("   - [CO2 Evitado Simulado (kg)] ou [CO2 Evitado Simulado (t)]")
    print("   - [Economia Simulada (R$)]")
    print()
    print("Exemplo com taxas reais do projeto (ano 2025):")
    print("  Input R$ 2.000 -> ~58,8 kg CO2 evitado | ~R$ 279 economia/ano")
    print()
    print("Taxas usadas (Total EcoLogix):")
    print("  CO2: 0,0294 kg por R$ investido")
    print("  Economia: R$ 0,1397 por R$ investido")
    print()
    print("Opcional: importe data/simulador_input.csv para slicer com valores fixos.")
    print("=" * 60)


if __name__ == "__main__":
    main()

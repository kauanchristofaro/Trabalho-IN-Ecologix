"""Gera EcoLogix Dashboard.pbix com 7 páginas de dashboards."""
import csv
import os
from pbix_mcp.builder import PBIXBuilder

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")


def read_csv(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_int(v):
    return int(v)


def to_float(v):
    return float(v)


def periodo_id(mes, ano):
    meses = {
        "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4, "Mai": 5, "Jun": 6,
        "Jul": 7, "Ago": 8, "Set": 9, "Out": 10, "Nov": 11, "Dez": 12,
    }
    return int(ano) * 100 + meses[mes]


def add_periodo(row):
    row["periodo_id"] = periodo_id(row["mes"], row["ano"])
    row["ano_mes"] = f"{row['ano']}-{periodo_id(row['mes'], row['ano']) % 100:02d}"
    return row


def main():
    calendario_rows = []
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    for ano in [2025]:
        for i, mes in enumerate(meses, 1):
            pid = ano * 100 + i
            calendario_rows.append({
                "periodo_id": pid,
                "mes": mes,
                "ano": ano,
                "ano_mes": f"{ano}-{i:02d}",
                "ordem": i,
            })

    entregas = []
    for r in read_csv("entregas_mensal.csv"):
        r = add_periodo(r)
        r["total_entregas"] = to_int(r["total_entregas"])
        r["entregas_sucesso_1a_tentativa"] = to_int(r["entregas_sucesso_1a_tentativa"])
        r["taxa_reentrega_pct"] = to_float(r["taxa_reentrega_pct"])
        r["tempo_medio_entrega_min"] = to_int(r["tempo_medio_entrega_min"])
        r["produtividade_entregador_dia"] = to_int(r["produtividade_entregador_dia"])
        r["distancia_media_km"] = to_float(r["distancia_media_km"])
        r["custo_medio_entrega_brl"] = to_float(r["custo_medio_entrega_brl"])
        r["custo_reentrega_brl"] = to_float(r["custo_reentrega_brl"])
        r["margem_lucro_entrega_brl"] = to_float(r["margem_lucro_entrega_brl"])
        entregas.append(r)

    regional = []
    for r in read_csv("entregas_regional.csv"):
        r = add_periodo(r)
        r["total_entregas"] = to_int(r["total_entregas"])
        r["taxa_sucesso_1a_tentativa_pct"] = to_int(r["taxa_sucesso_1a_tentativa_pct"])
        r["tempo_medio_entrega_min"] = to_int(r["tempo_medio_entrega_min"])
        r["produtividade_entregador_dia"] = to_int(r["produtividade_entregador_dia"])
        r["taxa_reentrega_pct"] = to_float(r["taxa_reentrega_pct"])
        regional.append(r)

    financeiro = []
    for r in read_csv("financeiro_mensal.csv"):
        r = add_periodo(r)
        for k in r:
            if k not in ("mes", "ano", "periodo_id", "ano_mes"):
                r[k] = to_float(r[k]) if "." in str(r[k]) else to_int(r[k])
        financeiro.append(r)

    sustentabilidade = []
    for r in read_csv("sustentabilidade_mensal.csv"):
        r = add_periodo(r)
        for k in r:
            if k not in ("mes", "ano", "periodo_id", "ano_mes"):
                r[k] = to_float(r[k]) if "." in str(r[k]) else to_int(r[k])
        sustentabilidade.append(r)

    clientes = []
    for r in read_csv("clientes_mensal.csv"):
        r = add_periodo(r)
        r["nps"] = to_int(r["nps"])
        r["avaliacao_media"] = to_float(r["avaliacao_media"])
        r["taxa_reclamacoes_pct"] = to_float(r["taxa_reclamacoes_pct"])
        r["entregas_avaliadas"] = to_int(r["entregas_avaliadas"])
        r["clientes_ativos"] = to_int(r["clientes_ativos"])
        clientes.append(r)

    comparativo = []
    for r in read_csv("comparativo_empresas_mensal.csv"):
        r = add_periodo(r)
        r["frota_veiculos"] = to_int(r["frota_veiculos"])
        r["km_mes_frota"] = to_int(r["km_mes_frota"])
        r["tarifa_kwh"] = to_float(r["tarifa_kwh"])
        r["kwh_consumo_mes"] = to_int(r["kwh_consumo_mes"])
        r["faturamento_brl"] = to_int(r["faturamento_brl"])
        r["custo_combustivel_brl"] = to_int(r["custo_combustivel_brl"])
        r["custo_manutencao_brl"] = to_int(r["custo_manutencao_brl"])
        r["emissao_co2_toneladas"] = to_float(r["emissao_co2_toneladas"])
        r["total_entregas"] = to_int(r["total_entregas"])
        r["margem_operacional_pct"] = to_float(r["margem_operacional_pct"])
        comparativo.append(r)

    comparativo_serie = []
    for r in read_csv("comparativo_serie.csv"):
        r["periodo_id"] = to_int(r["periodo_id"])
        r["ano"] = to_int(r["ano"])
        r["ordem"] = to_int(r["ordem"])
        r["faturamento_ecologix"] = to_int(r["faturamento_ecologix"])
        r["faturamento_logitrans"] = to_int(r["faturamento_logitrans"])
        r["combustivel_ecologix"] = to_int(r["combustivel_ecologix"])
        r["combustivel_logitrans"] = to_int(r["combustivel_logitrans"])
        r["manutencao_ecologix"] = to_int(r["manutencao_ecologix"])
        r["manutencao_logitrans"] = to_int(r["manutencao_logitrans"])
        r["co2_ecologix"] = to_float(r["co2_ecologix"])
        r["co2_logitrans"] = to_float(r["co2_logitrans"])
        comparativo_serie.append(r)

    energia_semestre = []
    for r in read_csv("energia_solar_semestral_wide.csv"):
        r["semestre_ordem"] = to_int(r["semestre_ordem"])
        r["semestre_id"] = to_int(r["semestre_id"])
        r["ano"] = to_int(r["ano"])
        r["semestre"] = to_int(r["semestre"])
        r["tarifa_media_kwh"] = to_float(r["tarifa_media_kwh"])
        for k in [
            "custo_semestral_sem", "custo_semestral_com",
            "custo_fixo_medio_sem", "custo_fixo_medio_com",
            "custo_acumulado_sem", "custo_acumulado_com",
            "economia_semestral", "economia_acumulada", "roi_atingido",
        ]:
            r[k] = to_int(r[k])
        energia_semestre.append(r)

    paineis_config = []
    for r in read_csv("paineis_solares_config.csv"):
        for k in r:
            r[k] = to_float(r[k]) if "." in str(r[k]) else to_int(r[k])
        paineis_config.append(r)

    calendario_semestre_rows = [
        {
            "semestre_ordem": r["semestre_ordem"],
            "semestre_id": r["semestre_id"],
            "semestre_label": r["semestre_label"],
            "ano": r["ano"],
            "semestre": r["semestre"],
        }
        for r in energia_semestre
    ]

    empresas = []
    for r in read_csv("empresas.csv"):
        r["empresa_id"] = to_int(r["empresa_id"])
        r["frota_veiculos"] = to_int(r["frota_veiculos"])
        r["ano_fundacao"] = to_int(r["ano_fundacao"])
        empresas.append(r)

    roi_resumo = []
    for r in read_csv("roi_investimento.csv"):
        r["categoria_id"] = to_int(r["categoria_id"])
        r["investimento_brl"] = to_int(r["investimento_brl"])
        r["economia_anual_brl"] = to_int(r["economia_anual_brl"])
        r["co2_evitado_anual_t"] = to_float(r["co2_evitado_anual_t"])
        r["reais_por_real_investido"] = to_float(r["reais_por_real_investido"])
        r["co2_kg_por_real"] = to_float(r["co2_kg_por_real"])
        r["co2_t_por_real"] = to_float(r["co2_t_por_real"])
        r["payback_anos"] = to_float(r["payback_anos"])
        r["roi_anual_pct"] = to_float(r["roi_anual_pct"])
        r["economia_mensal_media_brl"] = to_int(r["economia_mensal_media_brl"])
        roi_resumo.append(r)

    roi_mensal = []
    for r in read_csv("roi_investimento_mensal.csv"):
        r = add_periodo(r)
        r["periodo_id"] = to_int(r["periodo_id"])
        r["ano"] = to_int(r["ano"])
        r["economia_mensal_brl"] = to_int(r["economia_mensal_brl"])
        r["co2_evitado_mensal_kg"] = to_float(r["co2_evitado_mensal_kg"])
        r["economia_acumulada_brl"] = to_int(r["economia_acumulada_brl"])
        r["co2_evitado_acumulado_kg"] = to_float(r["co2_evitado_acumulado_kg"])
        r["investimento_brl"] = to_int(r["investimento_brl"])
        r["reais_economia_por_real_acum"] = to_float(r["reais_economia_por_real_acum"])
        r["co2_t_por_real_acum"] = to_float(r["co2_t_por_real_acum"])
        roi_mensal.append(r)

    simulador_taxas = []
    for r in read_csv("simulador_taxas.csv"):
        r["taxa_id"] = to_int(r["taxa_id"])
        r["co2_kg_por_real"] = to_float(r["co2_kg_por_real"])
        r["economia_por_real"] = to_float(r["economia_por_real"])
        r["despesa_ecologix_por_real"] = to_float(r["despesa_ecologix_por_real"])
        r["despesa_logitrans_por_real"] = to_float(r["despesa_logitrans_por_real"])
        r["co2_kg_emitido_ecologix_por_real"] = to_float(r["co2_kg_emitido_ecologix_por_real"])
        r["co2_kg_emitido_logitrans_por_real"] = to_float(r["co2_kg_emitido_logitrans_por_real"])
        r["investimento_referencia_brl"] = to_int(r["investimento_referencia_brl"])
        r["custo_anual_ecologix_brl"] = to_int(r["custo_anual_ecologix_brl"])
        r["custo_anual_logitrans_brl"] = to_int(r["custo_anual_logitrans_brl"])
        r["co2_anual_ecologix_t"] = to_float(r["co2_anual_ecologix_t"])
        r["co2_anual_logitrans_t"] = to_float(r["co2_anual_logitrans_t"])
        simulador_taxas.append(r)

    simulador_input = []
    for r in read_csv("simulador_input.csv"):
        r["valor_reais"] = to_int(r["valor_reais"])
        simulador_input.append(r)

    b = PBIXBuilder("EcoLogix Solutions - Dashboard BI")

    b.add_table("Calendario", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "ano_mes", "data_type": "String"},
        {"name": "ordem", "data_type": "Int64"},
    ], rows=calendario_rows)

    b.add_table("EntregasMensal", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "total_entregas", "data_type": "Int64"},
        {"name": "entregas_sucesso_1a_tentativa", "data_type": "Int64"},
        {"name": "taxa_reentrega_pct", "data_type": "Double"},
        {"name": "tempo_medio_entrega_min", "data_type": "Int64"},
        {"name": "produtividade_entregador_dia", "data_type": "Int64"},
        {"name": "distancia_media_km", "data_type": "Double"},
        {"name": "custo_medio_entrega_brl", "data_type": "Double"},
        {"name": "custo_reentrega_brl", "data_type": "Double"},
        {"name": "margem_lucro_entrega_brl", "data_type": "Double"},
    ], rows=entregas, source_csv=os.path.join(DATA, "entregas_mensal.csv"))

    b.add_table("EntregasRegional", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "regiao", "data_type": "String"},
        {"name": "total_entregas", "data_type": "Int64"},
        {"name": "taxa_sucesso_1a_tentativa_pct", "data_type": "Int64"},
        {"name": "tempo_medio_entrega_min", "data_type": "Int64"},
        {"name": "produtividade_entregador_dia", "data_type": "Int64"},
        {"name": "taxa_reentrega_pct", "data_type": "Double"},
    ], rows=regional, source_csv=os.path.join(DATA, "entregas_regional.csv"))

    b.add_table("FinanceiroMensal", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "receita_total_brl", "data_type": "Int64"},
        {"name": "custo_operacional_brl", "data_type": "Int64"},
        {"name": "margem_lucro_operacional_pct", "data_type": "Double"},
        {"name": "custo_medio_entrega_brl", "data_type": "Double"},
        {"name": "custo_reentrega_total_brl", "data_type": "Int64"},
        {"name": "margem_lucro_entrega_brl", "data_type": "Double"},
        {"name": "custo_energia_rota_brl", "data_type": "Double"},
    ], rows=financeiro, source_csv=os.path.join(DATA, "financeiro_mensal.csv"))

    b.add_table("SustentabilidadeMensal", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "co2_evitado_toneladas", "data_type": "Double"},
        {"name": "consumo_kwh_km", "data_type": "Double"},
        {"name": "frota_eletrica_pct", "data_type": "Int64"},
        {"name": "modais_sustentaveis_pct", "data_type": "Int64"},
        {"name": "custo_energia_rota_brl", "data_type": "Double"},
        {"name": "emissao_co2_por_entrega_g", "data_type": "Int64"},
    ], rows=sustentabilidade, source_csv=os.path.join(DATA, "sustentabilidade_mensal.csv"))

    b.add_table("ClientesMensal", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "nps", "data_type": "Int64"},
        {"name": "avaliacao_media", "data_type": "Double"},
        {"name": "taxa_reclamacoes_pct", "data_type": "Double"},
        {"name": "entregas_avaliadas", "data_type": "Int64"},
        {"name": "clientes_ativos", "data_type": "Int64"},
    ], rows=clientes, source_csv=os.path.join(DATA, "clientes_mensal.csv"))

    b.add_table("ComparativoEmpresas", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "empresa", "data_type": "String"},
        {"name": "tipo_frota", "data_type": "String"},
        {"name": "frota_veiculos", "data_type": "Int64"},
        {"name": "km_mes_frota", "data_type": "Int64"},
        {"name": "bandeira_tarifaria", "data_type": "String"},
        {"name": "tarifa_kwh", "data_type": "Double"},
        {"name": "kwh_consumo_mes", "data_type": "Int64"},
        {"name": "receita_total_brl", "data_type": "Int64"},
        {"name": "faturamento_brl", "data_type": "Int64"},
        {"name": "custo_combustivel_brl", "data_type": "Int64"},
        {"name": "custo_manutencao_brl", "data_type": "Int64"},
        {"name": "emissao_co2_toneladas", "data_type": "Double"},
        {"name": "co2_por_entrega_g", "data_type": "Int64"},
        {"name": "total_entregas", "data_type": "Int64"},
        {"name": "custo_medio_entrega_brl", "data_type": "Double"},
        {"name": "margem_lucro_entrega_brl", "data_type": "Double"},
        {"name": "margem_operacional_pct", "data_type": "Double"},
        {"name": "frota_combustao_pct", "data_type": "Int64"},
    ], rows=comparativo, source_csv=os.path.join(DATA, "comparativo_empresas_mensal.csv"))

    b.add_table("ComparativoSerie", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "ano_mes", "data_type": "String"},
        {"name": "ordem", "data_type": "Int64"},
        {"name": "faturamento_ecologix", "data_type": "Int64"},
        {"name": "faturamento_logitrans", "data_type": "Int64"},
        {"name": "combustivel_ecologix", "data_type": "Int64"},
        {"name": "combustivel_logitrans", "data_type": "Int64"},
        {"name": "manutencao_ecologix", "data_type": "Int64"},
        {"name": "manutencao_logitrans", "data_type": "Int64"},
        {"name": "co2_ecologix", "data_type": "Double"},
        {"name": "co2_logitrans", "data_type": "Double"},
    ], rows=comparativo_serie, source_csv=os.path.join(DATA, "comparativo_serie.csv"))

    b.add_table("CalendarioSemestre", [
        {"name": "semestre_ordem", "data_type": "Int64"},
        {"name": "semestre_id", "data_type": "Int64"},
        {"name": "semestre_label", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "semestre", "data_type": "Int64"},
    ], rows=calendario_semestre_rows)

    b.add_table("EnergiaSolarSemestre", [
        {"name": "semestre_ordem", "data_type": "Int64"},
        {"name": "semestre_id", "data_type": "Int64"},
        {"name": "semestre_label", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "semestre", "data_type": "Int64"},
        {"name": "bandeira_tarifaria", "data_type": "String"},
        {"name": "tarifa_media_kwh", "data_type": "Double"},
        {"name": "custo_semestral_sem", "data_type": "Int64"},
        {"name": "custo_semestral_com", "data_type": "Int64"},
        {"name": "custo_fixo_medio_sem", "data_type": "Int64"},
        {"name": "custo_fixo_medio_com", "data_type": "Int64"},
        {"name": "custo_acumulado_sem", "data_type": "Int64"},
        {"name": "custo_acumulado_com", "data_type": "Int64"},
        {"name": "economia_semestral", "data_type": "Int64"},
        {"name": "economia_acumulada", "data_type": "Int64"},
        {"name": "roi_atingido", "data_type": "Int64"},
    ], rows=energia_semestre, source_csv=os.path.join(DATA, "energia_solar_semestral_wide.csv"))

    b.add_table("PaineisSolaresConfig", [
        {"name": "frota_veiculos", "data_type": "Int64"},
        {"name": "km_dia_veiculo", "data_type": "Int64"},
        {"name": "qtd_paineis", "data_type": "Int64"},
        {"name": "potencia_painel_w", "data_type": "Int64"},
        {"name": "potencia_total_kwp", "data_type": "Double"},
        {"name": "kwh_dia_por_painel", "data_type": "Double"},
        {"name": "kwh_geracao_solar_mes", "data_type": "Int64"},
        {"name": "kwh_mes_frota", "data_type": "Int64"},
        {"name": "custo_instalacao_brl", "data_type": "Int64"},
        {"name": "cobertura_solar_pct", "data_type": "Int64"},
        {"name": "economia_mensal_media_brl", "data_type": "Int64"},
        {"name": "mes_roi", "data_type": "Int64"},
        {"name": "semestre_roi", "data_type": "Int64"},
    ], rows=paineis_config, source_csv=os.path.join(DATA, "paineis_solares_config.csv"))

    b.add_table("Empresas", [
        {"name": "empresa_id", "data_type": "Int64"},
        {"name": "empresa", "data_type": "String"},
        {"name": "tipo_frota", "data_type": "String"},
        {"name": "cidade_sede", "data_type": "String"},
        {"name": "frota_veiculos", "data_type": "Int64"},
        {"name": "ano_fundacao", "data_type": "Int64"},
        {"name": "descricao", "data_type": "String"},
    ], rows=empresas, source_csv=os.path.join(DATA, "empresas.csv"))

    b.add_table("RoiInvestimento", [
        {"name": "categoria_id", "data_type": "Int64"},
        {"name": "categoria", "data_type": "String"},
        {"name": "tipo_tecnologia", "data_type": "String"},
        {"name": "referencia_convencional", "data_type": "String"},
        {"name": "investimento_brl", "data_type": "Int64"},
        {"name": "economia_anual_brl", "data_type": "Int64"},
        {"name": "co2_evitado_anual_t", "data_type": "Double"},
        {"name": "reais_por_real_investido", "data_type": "Double"},
        {"name": "co2_kg_por_real", "data_type": "Double"},
        {"name": "co2_t_por_real", "data_type": "Double"},
        {"name": "payback_anos", "data_type": "Double"},
        {"name": "roi_anual_pct", "data_type": "Double"},
        {"name": "economia_mensal_media_brl", "data_type": "Int64"},
    ], rows=roi_resumo, source_csv=os.path.join(DATA, "roi_investimento.csv"))

    b.add_table("RoiInvestimentoMensal", [
        {"name": "periodo_id", "data_type": "Int64"},
        {"name": "mes", "data_type": "String"},
        {"name": "ano", "data_type": "Int64"},
        {"name": "categoria", "data_type": "String"},
        {"name": "economia_mensal_brl", "data_type": "Int64"},
        {"name": "co2_evitado_mensal_kg", "data_type": "Double"},
        {"name": "economia_acumulada_brl", "data_type": "Int64"},
        {"name": "co2_evitado_acumulado_kg", "data_type": "Double"},
        {"name": "investimento_brl", "data_type": "Int64"},
        {"name": "reais_economia_por_real_acum", "data_type": "Double"},
        {"name": "co2_t_por_real_acum", "data_type": "Double"},
    ], rows=roi_mensal, source_csv=os.path.join(DATA, "roi_investimento_mensal.csv"))

    b.add_table("SimuladorTaxas", [
        {"name": "taxa_id", "data_type": "Int64"},
        {"name": "descricao", "data_type": "String"},
        {"name": "co2_kg_por_real", "data_type": "Double"},
        {"name": "economia_por_real", "data_type": "Double"},
        {"name": "despesa_ecologix_por_real", "data_type": "Double"},
        {"name": "despesa_logitrans_por_real", "data_type": "Double"},
        {"name": "co2_kg_emitido_ecologix_por_real", "data_type": "Double"},
        {"name": "co2_kg_emitido_logitrans_por_real", "data_type": "Double"},
        {"name": "investimento_referencia_brl", "data_type": "Int64"},
        {"name": "custo_anual_ecologix_brl", "data_type": "Int64"},
        {"name": "custo_anual_logitrans_brl", "data_type": "Int64"},
        {"name": "co2_anual_ecologix_t", "data_type": "Double"},
        {"name": "co2_anual_logitrans_t", "data_type": "Double"},
    ], rows=simulador_taxas, source_csv=os.path.join(DATA, "simulador_taxas.csv"))

    b.add_table("SimuladorInput", [
        {"name": "valor_reais", "data_type": "Int64"},
        {"name": "rotulo", "data_type": "String"},
    ], rows=simulador_input, source_csv=os.path.join(DATA, "simulador_input.csv"))

    for tbl in [
        "EntregasMensal", "EntregasRegional", "FinanceiroMensal",
        "SustentabilidadeMensal", "ClientesMensal", "ComparativoEmpresas",
        "ComparativoSerie", "RoiInvestimentoMensal",
    ]:
        b.add_relationship(tbl, "periodo_id", "Calendario", "periodo_id")
    b.add_relationship("ComparativoEmpresas", "empresa", "Empresas", "empresa")
    b.add_relationship("EnergiaSolarSemestre", "semestre_ordem", "CalendarioSemestre", "semestre_ordem")

    b.add_measure("ComparativoEmpresas", "Frota Veiculos", "MAX(ComparativoEmpresas[frota_veiculos])")
    b.add_measure("EntregasMensal", "Total Entregas", "SUM(EntregasMensal[total_entregas])")
    b.add_measure("EntregasMensal", "Taxa Reentrega Media", "AVERAGE(EntregasMensal[taxa_reentrega_pct])")
    b.add_measure("EntregasMensal", "Tempo Medio Entrega", "AVERAGE(EntregasMensal[tempo_medio_entrega_min])")
    b.add_measure("EntregasMensal", "Produtividade Media", "AVERAGE(EntregasMensal[produtividade_entregador_dia])")
    b.add_measure("EntregasRegional", "Entregas por Regiao", "SUM(EntregasRegional[total_entregas])")
    b.add_measure("EntregasRegional", "Reentrega Regional Media", "AVERAGE(EntregasRegional[taxa_reentrega_pct])")
    b.add_measure("FinanceiroMensal", "Margem Operacional Media", "AVERAGE(FinanceiroMensal[margem_lucro_operacional_pct])")
    b.add_measure("FinanceiroMensal", "Custo Medio Entrega", "AVERAGE(FinanceiroMensal[custo_medio_entrega_brl])")
    b.add_measure("FinanceiroMensal", "Margem Lucro Entrega", "AVERAGE(FinanceiroMensal[margem_lucro_entrega_brl])")
    b.add_measure("FinanceiroMensal", "Receita Total", "SUM(FinanceiroMensal[receita_total_brl])")
    b.add_measure("SustentabilidadeMensal", "CO2 Evitado Total", "SUM(SustentabilidadeMensal[co2_evitado_toneladas])")
    b.add_measure("SustentabilidadeMensal", "CO2 por Entrega", "AVERAGE(SustentabilidadeMensal[emissao_co2_por_entrega_g])")
    b.add_measure("SustentabilidadeMensal", "Frota Eletrica Media", "AVERAGE(SustentabilidadeMensal[frota_eletrica_pct])")
    b.add_measure("SustentabilidadeMensal", "Modais Sustentaveis Media", "AVERAGE(SustentabilidadeMensal[modais_sustentaveis_pct])")
    b.add_measure("ClientesMensal", "NPS Medio", "AVERAGE(ClientesMensal[nps])")
    b.add_measure("ClientesMensal", "Avaliacao Media", "AVERAGE(ClientesMensal[avaliacao_media])")
    b.add_measure("ClientesMensal", "Taxa Reclamacoes Media", "AVERAGE(ClientesMensal[taxa_reclamacoes_pct])")

    b.add_measure("ComparativoEmpresas", "Faturamento Total", "SUM(ComparativoEmpresas[faturamento_brl])")
    b.add_measure("ComparativoEmpresas", "Custo Combustivel Total", "SUM(ComparativoEmpresas[custo_combustivel_brl])")
    b.add_measure("ComparativoEmpresas", "Custo Manutencao Total", "SUM(ComparativoEmpresas[custo_manutencao_brl])")
    b.add_measure("ComparativoEmpresas", "Emissao CO2 Total", "SUM(ComparativoEmpresas[emissao_co2_toneladas])")
    b.add_measure("ComparativoEmpresas", "Margem Comparativa Media", "AVERAGE(ComparativoEmpresas[margem_operacional_pct])")

    b.add_measure(
        "ComparativoEmpresas", "Faturamento EcoLogix",
        'CALCULATE(SUM(ComparativoEmpresas[faturamento_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Faturamento LogiTrans",
        'CALCULATE(SUM(ComparativoEmpresas[faturamento_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Combustivel EcoLogix",
        'CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Combustivel LogiTrans",
        'CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Manutencao EcoLogix",
        'CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Manutencao LogiTrans",
        'CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    )
    b.add_measure(
        "ComparativoEmpresas", "CO2 EcoLogix",
        'CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "CO2 LogiTrans",
        'CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Economia Combustivel",
        'CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Reducao CO2",
        'CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Economia Manutencao",
        'CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Economia Operacional vs LogiTrans",
        'CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") + CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") - CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")',
    )
    b.add_measure(
        "ComparativoEmpresas", "Custo Total Logitrans",
        'CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") + CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express")',
    )
    b.add_measure(
        "ComparativoEmpresas", "CO2 Emitido por Real Logitrans",
        'DIVIDE(CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "LogiTrans Express") * 1000, [Custo Total Logitrans])',
    )
    b.add_measure(
        "ComparativoEmpresas", "CO2 Evitado por Real EcoLogix",
        'VAR InvestimentoEcoLogix = 3750000 VAR CO2FrotaKg = (CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[emissao_co2_toneladas]), ComparativoEmpresas[empresa] = "EcoLogix Solutions")) * 1000 VAR Meses = CALCULATE(DISTINCTCOUNT(ComparativoEmpresas[periodo_id]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") VAR CO2SolarKg = Meses * 435.6 RETURN DIVIDE(CO2FrotaKg + CO2SolarKg, InvestimentoEcoLogix)',
    )
    b.add_measure(
        "ComparativoEmpresas", "Economia Total por Real EcoLogix",
        'VAR InvestimentoEcoLogix = 3750000 VAR EconomiaFrota = CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") + CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "LogiTrans Express") - CALCULATE(SUM(ComparativoEmpresas[custo_combustivel_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") - CALCULATE(SUM(ComparativoEmpresas[custo_manutencao_brl]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") VAR Meses = CALCULATE(DISTINCTCOUNT(ComparativoEmpresas[periodo_id]), ComparativoEmpresas[empresa] = "EcoLogix Solutions") VAR EconomiaSolar = Meses * 3431 RETURN DIVIDE(EconomiaFrota + EconomiaSolar, InvestimentoEcoLogix)',
    )

    b.add_measure("ComparativoSerie", "Fat Eco Serie", "SUM(ComparativoSerie[faturamento_ecologix])")
    b.add_measure("ComparativoSerie", "Fat Logi Serie", "SUM(ComparativoSerie[faturamento_logitrans])")
    b.add_measure("ComparativoSerie", "Comb Eco Serie", "SUM(ComparativoSerie[combustivel_ecologix])")
    b.add_measure("ComparativoSerie", "Comb Logi Serie", "SUM(ComparativoSerie[combustivel_logitrans])")
    b.add_measure("ComparativoSerie", "Manut Eco Serie", "SUM(ComparativoSerie[manutencao_ecologix])")
    b.add_measure("ComparativoSerie", "Manut Logi Serie", "SUM(ComparativoSerie[manutencao_logitrans])")

    b.add_measure("EnergiaSolarSemestre", "Custo Semestral Sem Painel", "SUM(EnergiaSolarSemestre[custo_semestral_sem])")
    b.add_measure("EnergiaSolarSemestre", "Custo Semestral Com Painel", "SUM(EnergiaSolarSemestre[custo_semestral_com])")
    b.add_measure("EnergiaSolarSemestre", "Custo Fixo Medio Sem", "AVERAGE(EnergiaSolarSemestre[custo_fixo_medio_sem])")
    b.add_measure("EnergiaSolarSemestre", "Custo Fixo Medio Com", "AVERAGE(EnergiaSolarSemestre[custo_fixo_medio_com])")
    b.add_measure("EnergiaSolarSemestre", "Acumulado Sem Painel", "MAX(EnergiaSolarSemestre[custo_acumulado_sem])")
    b.add_measure("EnergiaSolarSemestre", "Acumulado Com Painel", "MAX(EnergiaSolarSemestre[custo_acumulado_com])")
    b.add_measure("EnergiaSolarSemestre", "Economia Acumulada", "MAX(EnergiaSolarSemestre[economia_acumulada])")
    b.add_measure("EnergiaSolarSemestre", "Economia Semestral", "SUM(EnergiaSolarSemestre[economia_semestral])")
    b.add_measure("PaineisSolaresConfig", "Qtd Paineis", "MAX(PaineisSolaresConfig[qtd_paineis])")
    b.add_measure("PaineisSolaresConfig", "Potencia Total kWp", "MAX(PaineisSolaresConfig[potencia_total_kwp])")
    b.add_measure("PaineisSolaresConfig", "Investimento Solar", "MAX(PaineisSolaresConfig[custo_instalacao_brl])")
    b.add_measure("PaineisSolaresConfig", "Economia Mensal Media", "MAX(PaineisSolaresConfig[economia_mensal_media_brl])")
    b.add_measure("PaineisSolaresConfig", "Cobertura Solar Pct", "MAX(PaineisSolaresConfig[cobertura_solar_pct])")
    b.add_measure("PaineisSolaresConfig", "Semestre ROI", "MAX(PaineisSolaresConfig[semestre_roi])")

    b.add_measure(
        "RoiInvestimento", "Investimento Total ROI",
        'CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2)',
    )
    b.add_measure(
        "RoiInvestimento", "Economia Anual ROI",
        'CALCULATE(SUM(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria_id] <= 2)',
    )
    b.add_measure(
        "RoiInvestimento", "CO2 Evitado Anual ROI",
        'CALCULATE(SUM(RoiInvestimento[co2_evitado_anual_t]), RoiInvestimento[categoria_id] <= 2)',
    )
    b.add_measure(
        "RoiInvestimento", "Reais por Real Investido",
        'DIVIDE(CALCULATE(SUM(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria_id] <= 2), CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2))',
    )
    b.add_measure(
        "RoiInvestimento", "CO2 kg por Real",
        'DIVIDE(CALCULATE(SUM(RoiInvestimento[co2_evitado_anual_t]), RoiInvestimento[categoria_id] <= 2) * 1000, CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2))',
    )
    b.add_measure(
        "RoiInvestimento", "CO2 t por Real",
        'DIVIDE(CALCULATE(SUM(RoiInvestimento[co2_evitado_anual_t]), RoiInvestimento[categoria_id] <= 2), CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2))',
    )
    b.add_measure(
        "RoiInvestimento", "Payback Anos Consolidado",
        'DIVIDE(CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2), CALCULATE(SUM(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria_id] <= 2))',
    )
    b.add_measure(
        "RoiInvestimento", "ROI Anual Pct Consolidado",
        'DIVIDE(CALCULATE(SUM(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria_id] <= 2), CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2)) * 100',
    )
    b.add_measure(
        "RoiInvestimento", "Investimento Total EcoLogix",
        'CALCULATE(MAX(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria] = "Total EcoLogix")',
    )
    b.add_measure(
        "RoiInvestimento", "Economia Operacional Anual",
        'CALCULATE(MAX(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria] = "Total EcoLogix")',
    )
    b.add_measure(
        "RoiInvestimento", "CO2 Evitado Total Anual",
        'CALCULATE(MAX(RoiInvestimento[co2_evitado_anual_t]), RoiInvestimento[categoria] = "Total EcoLogix")',
    )
    b.add_measure(
        "RoiInvestimento", "Reais por Real Frota",
        'CALCULATE(AVERAGE(RoiInvestimento[reais_por_real_investido]), RoiInvestimento[categoria] = "Frota Eletrica")',
    )
    b.add_measure(
        "RoiInvestimento", "Reais por Real Solar",
        'CALCULATE(AVERAGE(RoiInvestimento[reais_por_real_investido]), RoiInvestimento[categoria] = "Energia Solar")',
    )
    b.add_measure(
        "RoiInvestimento", "CO2 kg por Real Frota",
        'CALCULATE(AVERAGE(RoiInvestimento[co2_kg_por_real]), RoiInvestimento[categoria] = "Frota Eletrica")',
    )
    b.add_measure(
        "RoiInvestimento", "CO2 kg por Real Solar",
        'CALCULATE(AVERAGE(RoiInvestimento[co2_kg_por_real]), RoiInvestimento[categoria] = "Energia Solar")',
    )
    b.add_measure(
        "RoiInvestimento", "Investimento Frota",
        'CALCULATE(MAX(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria] = "Frota Eletrica")',
    )
    b.add_measure(
        "RoiInvestimento", "Investimento Solar ROI",
        'CALCULATE(MAX(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria] = "Energia Solar")',
    )
    b.add_measure(
        "RoiInvestimento", "Economia Anual Frota",
        'CALCULATE(MAX(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria] = "Frota Eletrica")',
    )
    b.add_measure(
        "RoiInvestimento", "Economia Anual Solar",
        'CALCULATE(MAX(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria] = "Energia Solar")',
    )

    b.add_measure(
        "RoiInvestimento", "CO2 Evitado por Real EcoLogix ROI",
        'DIVIDE(CALCULATE(SUM(RoiInvestimento[co2_evitado_anual_t]), RoiInvestimento[categoria_id] <= 2) * 1000, CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2))',
    )
    b.add_measure(
        "RoiInvestimento", "Economia Total por Real EcoLogix ROI",
        'DIVIDE(CALCULATE(SUM(RoiInvestimento[economia_anual_brl]), RoiInvestimento[categoria_id] <= 2), CALCULATE(SUM(RoiInvestimento[investimento_brl]), RoiInvestimento[categoria_id] <= 2))',
    )

    b.add_measure("RoiInvestimentoMensal", "Economia Mensal ROI", "SUM(RoiInvestimentoMensal[economia_mensal_brl])")
    b.add_measure("RoiInvestimentoMensal", "Economia Acumulada ROI", "MAX(RoiInvestimentoMensal[economia_acumulada_brl])")
    b.add_measure("RoiInvestimentoMensal", "CO2 Evitado Mensal kg", "SUM(RoiInvestimentoMensal[co2_evitado_mensal_kg])")
    b.add_measure("RoiInvestimentoMensal", "CO2 Acumulado kg", "MAX(RoiInvestimentoMensal[co2_evitado_acumulado_kg])")
    b.add_measure(
        "RoiInvestimentoMensal", "Economia Acum Frota",
        'CALCULATE(MAX(RoiInvestimentoMensal[economia_acumulada_brl]), RoiInvestimentoMensal[categoria] = "Frota Eletrica")',
    )
    b.add_measure(
        "RoiInvestimentoMensal", "Economia Acum Solar",
        'CALCULATE(MAX(RoiInvestimentoMensal[economia_acumulada_brl]), RoiInvestimentoMensal[categoria] = "Energia Solar")',
    )
    b.add_measure(
        "RoiInvestimentoMensal", "CO2 Acum Frota kg",
        'CALCULATE(MAX(RoiInvestimentoMensal[co2_evitado_acumulado_kg]), RoiInvestimentoMensal[categoria] = "Frota Eletrica")',
    )
    b.add_measure(
        "RoiInvestimentoMensal", "CO2 Acum Solar kg",
        'CALCULATE(MAX(RoiInvestimentoMensal[co2_evitado_acumulado_kg]), RoiInvestimentoMensal[categoria] = "Energia Solar")',
    )
    b.add_measure(
        "RoiInvestimentoMensal", "Reais Economia por Real Acum",
        'CALCULATE(MAX(RoiInvestimentoMensal[reais_economia_por_real_acum]), RoiInvestimentoMensal[categoria] = "Total EcoLogix")',
    )
    b.add_measure(
        "RoiInvestimentoMensal", "CO2 t por Real Acum",
        'CALCULATE(MAX(RoiInvestimentoMensal[co2_t_por_real_acum]), RoiInvestimentoMensal[categoria] = "Total EcoLogix")',
    )
    b.add_measure(
        "RoiInvestimentoMensal", "Economia Acum Total",
        'CALCULATE(MAX(RoiInvestimentoMensal[economia_acumulada_brl]), RoiInvestimentoMensal[categoria] = "Total EcoLogix")',
    )

    b.add_measure("SimuladorInput", "Valor Investimento Selecionado", "SELECTEDVALUE(SimuladorInput[valor_reais], 0)")
    b.add_measure(
        "SimuladorInput", "Investimento Simulado (R$)",
        "IF(HASONEVALUE(SimuladorInput[valor_reais]), SELECTEDVALUE(SimuladorInput[valor_reais]), MIN(SimuladorInput[valor_reais]))",
    )
    b.add_measure(
        "SimuladorInput", "CO2 Evitado Simulado (kg)",
        "[Investimento Simulado (R$)] * MAX(SimuladorTaxas[co2_kg_por_real])",
    )
    b.add_measure(
        "SimuladorInput", "Economia Simulada (R$)",
        "[Investimento Simulado (R$)] * MAX(SimuladorTaxas[economia_por_real])",
    )
    b.add_measure("SimuladorInput", "CO2 Evitado Simulado (t)", "[CO2 Evitado Simulado (kg)] / 1000")
    b.add_measure(
        "SimuladorInput", "Despesas Estimadas EcoLogix (R$)",
        "[Investimento Simulado (R$)] * MAX(SimuladorTaxas[despesa_ecologix_por_real])",
    )
    b.add_measure(
        "SimuladorInput", "Despesas Estimadas LogiTrans (R$)",
        "[Investimento Simulado (R$)] * MAX(SimuladorTaxas[despesa_logitrans_por_real])",
    )
    b.add_measure(
        "SimuladorInput", "Diferenca Despesas LogiTrans vs EcoLogix (R$)",
        "[Despesas Estimadas LogiTrans (R$)] - [Despesas Estimadas EcoLogix (R$)]",
    )
    b.add_measure(
        "SimuladorInput", "Carbono Emitido EcoLogix (kg)",
        "[Investimento Simulado (R$)] * MAX(SimuladorTaxas[co2_kg_emitido_ecologix_por_real])",
    )
    b.add_measure(
        "SimuladorInput", "Carbono Emitido LogiTrans (kg)",
        "[Investimento Simulado (R$)] * MAX(SimuladorTaxas[co2_kg_emitido_logitrans_por_real])",
    )
    b.add_measure(
        "SimuladorInput", "Diferenca Carbono LogiTrans vs EcoLogix (kg)",
        "[Carbono Emitido LogiTrans (kg)] - [Carbono Emitido EcoLogix (kg)]",
    )
    b.add_measure("SimuladorTaxas", "Taxa CO2 kg por Real", "MAX(SimuladorTaxas[co2_kg_por_real])")
    b.add_measure("SimuladorTaxas", "Taxa Economia por Real", "MAX(SimuladorTaxas[economia_por_real])")

    b.add_page("Dashboard Executivo", [
        {"name": "nps_card", "type": "card", "x": 20, "y": 20, "width": 240, "height": 110,
         "config": {"measure": "NPS Medio"}},
        {"name": "margem_card", "type": "card", "x": 280, "y": 20, "width": 240, "height": 110,
         "config": {"measure": "Margem Operacional Media"}},
        {"name": "reentrega_card", "type": "card", "x": 540, "y": 20, "width": 240, "height": 110,
         "config": {"measure": "Taxa Reentrega Media"}},
        {"name": "co2_card", "type": "card", "x": 800, "y": 20, "width": 240, "height": 110,
         "config": {"measure": "CO2 Evitado Total"}},
        {"name": "entregas_card", "type": "card", "x": 1060, "y": 20, "width": 200, "height": 110,
         "config": {"measure": "Total Entregas"}},
        {"name": "nps_linha", "type": "lineChart", "x": 20, "y": 150, "width": 620, "height": 280,
         "config": {"category": {"table": "ClientesMensal", "column": "periodo_id"}, "measure": "NPS Medio"}},
        {"name": "margem_linha", "type": "lineChart", "x": 660, "y": 150, "width": 600, "height": 280,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Margem Operacional Media"}},
        {"name": "reentrega_linha", "type": "lineChart", "x": 20, "y": 450, "width": 620, "height": 250,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Taxa Reentrega Media"}},
        {"name": "co2_linha", "type": "lineChart", "x": 660, "y": 450, "width": 600, "height": 250,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "CO2 por Entrega"}},
    ])

    b.add_page("Dashboard Operacional", [
        {"name": "mes_slicer", "type": "slicer", "x": 20, "y": 20, "width": 220, "height": 100,
         "config": {"column": {"table": "Calendario", "column": "mes"}}},
        {"name": "regiao_slicer", "type": "slicer", "x": 260, "y": 20, "width": 280, "height": 100,
         "config": {"column": {"table": "EntregasRegional", "column": "regiao"}}},
        {"name": "tempo_card", "type": "card", "x": 560, "y": 20, "width": 220, "height": 100,
         "config": {"measure": "Tempo Medio Entrega"}},
        {"name": "prod_card", "type": "card", "x": 800, "y": 20, "width": 220, "height": 100,
         "config": {"measure": "Produtividade Media"}},
        {"name": "reentrega_op_card", "type": "card", "x": 1040, "y": 20, "width": 220, "height": 100,
         "config": {"measure": "Taxa Reentrega Media"}},
        {"name": "tempo_linha", "type": "lineChart", "x": 20, "y": 140, "width": 620, "height": 280,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Tempo Medio Entrega"}},
        {"name": "prod_linha", "type": "lineChart", "x": 660, "y": 140, "width": 600, "height": 280,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Produtividade Media"}},
        {"name": "regiao_bar", "type": "clusteredBarChart", "x": 20, "y": 440, "width": 620, "height": 260,
         "config": {"category": {"table": "EntregasRegional", "column": "regiao"}, "measure": "Entregas por Regiao"}},
        {"name": "reentrega_reg_bar", "type": "clusteredColumnChart", "x": 660, "y": 440, "width": 600, "height": 260,
         "config": {"category": {"table": "EntregasRegional", "column": "regiao"}, "measure": "Reentrega Regional Media"}},
    ])

    b.add_page("Dashboard Sustentabilidade", [
        {"name": "co2_evitado_card", "type": "card", "x": 20, "y": 20, "width": 300, "height": 110,
         "config": {"measure": "CO2 Evitado Total"}},
        {"name": "co2_entrega_card", "type": "card", "x": 340, "y": 20, "width": 300, "height": 110,
         "config": {"measure": "CO2 por Entrega"}},
        {"name": "frota_card", "type": "card", "x": 660, "y": 20, "width": 300, "height": 110,
         "config": {"measure": "Frota Eletrica Media"}},
        {"name": "modais_card", "type": "card", "x": 980, "y": 20, "width": 280, "height": 110,
         "config": {"measure": "Modais Sustentaveis Media"}},
        {"name": "co2_evitado_linha", "type": "lineChart", "x": 20, "y": 150, "width": 620, "height": 280,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "CO2 Evitado Total"}},
        {"name": "frota_linha", "type": "lineChart", "x": 660, "y": 150, "width": 600, "height": 280,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Frota Eletrica Media"}},
        {"name": "modais_pie", "type": "pieChart", "x": 20, "y": 450, "width": 480, "height": 260,
         "config": {"category": {"table": "Calendario", "column": "mes"}, "measure": "Modais Sustentaveis Media"}},
        {"name": "co2_entrega_col", "type": "clusteredColumnChart", "x": 520, "y": 450, "width": 740, "height": 260,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "CO2 por Entrega"}},
    ])

    b.add_page("Dashboard Financeiro", [
        {"name": "receita_card", "type": "card", "x": 20, "y": 20, "width": 280, "height": 110,
         "config": {"measure": "Receita Total"}},
        {"name": "margem_fin_card", "type": "card", "x": 320, "y": 20, "width": 280, "height": 110,
         "config": {"measure": "Margem Operacional Media"}},
        {"name": "custo_card", "type": "card", "x": 620, "y": 20, "width": 280, "height": 110,
         "config": {"measure": "Custo Medio Entrega"}},
        {"name": "margem_ent_card", "type": "card", "x": 920, "y": 20, "width": 280, "height": 110,
         "config": {"measure": "Margem Lucro Entrega"}},
        {"name": "margem_linha_fin", "type": "lineChart", "x": 20, "y": 150, "width": 620, "height": 280,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Margem Operacional Media"}},
        {"name": "custo_linha", "type": "lineChart", "x": 660, "y": 150, "width": 600, "height": 280,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Custo Medio Entrega"}},
        {"name": "receita_bar", "type": "clusteredColumnChart", "x": 20, "y": 450, "width": 620, "height": 260,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Receita Total"}},
        {"name": "margem_ent_bar", "type": "clusteredColumnChart", "x": 660, "y": 450, "width": 600, "height": 260,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Margem Lucro Entrega"}},
    ])

    b.add_page("Dashboard Comparativo", [
        {"name": "economia_op_card", "type": "card", "x": 540, "y": 20, "width": 240, "height": 90,
         "config": {"measure": "Economia Operacional vs Logitrans"}},
        {"name": "inv_eco_card", "type": "card", "x": 800, "y": 20, "width": 220, "height": 90,
         "config": {"measure": "Investimento Total EcoLogix"}},
        {"name": "co2_real_card", "type": "card", "x": 1040, "y": 20, "width": 220, "height": 90,
         "config": {"measure": "CO2 t por Real"}},
        {"name": "mes_comp_slicer", "type": "slicer", "x": 20, "y": 20, "width": 200, "height": 90,
         "config": {"column": {"table": "Calendario", "column": "mes"}}},
        {"name": "empresa_comp_slicer", "type": "slicer", "x": 240, "y": 20, "width": 280, "height": 90,
         "config": {"column": {"table": "ComparativoEmpresas", "column": "empresa"}}},
        {"name": "economia_comb_card", "type": "card", "x": 540, "y": 125, "width": 220, "height": 90,
         "config": {"measure": "Economia Combustivel"}},
        {"name": "reducao_co2_card", "type": "card", "x": 780, "y": 125, "width": 220, "height": 90,
         "config": {"measure": "Reducao CO2"}},
        {"name": "margem_comp_card", "type": "card", "x": 1020, "y": 125, "width": 240, "height": 90,
         "config": {"measure": "Margem Comparativa Media"}},
        {"name": "fat_eco_card", "type": "card", "x": 20, "y": 230, "width": 200, "height": 85,
         "config": {"measure": "Faturamento EcoLogix"}},
        {"name": "fat_logi_card", "type": "card", "x": 240, "y": 230, "width": 200, "height": 85,
         "config": {"measure": "Faturamento LogiTrans"}},
        {"name": "comb_eco_card", "type": "card", "x": 460, "y": 230, "width": 200, "height": 85,
         "config": {"measure": "Combustivel EcoLogix"}},
        {"name": "comb_logi_card", "type": "card", "x": 680, "y": 230, "width": 200, "height": 85,
         "config": {"measure": "Combustivel LogiTrans"}},
        {"name": "manut_eco_card", "type": "card", "x": 900, "y": 230, "width": 180, "height": 85,
         "config": {"measure": "Manutencao EcoLogix"}},
        {"name": "manut_logi_card", "type": "card", "x": 1100, "y": 230, "width": 160, "height": 85,
         "config": {"measure": "Manutencao LogiTrans"}},
        {"name": "fat_comp_bar", "type": "clusteredBarChart", "x": 20, "y": 330, "width": 300, "height": 200,
         "config": {"category": {"table": "ComparativoEmpresas", "column": "empresa"}, "measure": "Faturamento Total"}},
        {"name": "comb_comp_bar", "type": "clusteredBarChart", "x": 340, "y": 330, "width": 300, "height": 200,
         "config": {"category": {"table": "ComparativoEmpresas", "column": "empresa"}, "measure": "Custo Combustivel Total"}},
        {"name": "manut_comp_bar", "type": "clusteredBarChart", "x": 660, "y": 330, "width": 300, "height": 200,
         "config": {"category": {"table": "ComparativoEmpresas", "column": "empresa"}, "measure": "Custo Manutencao Total"}},
        {"name": "co2_comp_bar", "type": "clusteredBarChart", "x": 980, "y": 330, "width": 280, "height": 200,
         "config": {"category": {"table": "ComparativoEmpresas", "column": "empresa"}, "measure": "Emissao CO2 Total"}},
        {"name": "fat_eco_linha", "type": "lineChart", "x": 20, "y": 545, "width": 620, "height": 130,
         "config": {"category": {"table": "ComparativoSerie", "column": "ano_mes"}, "measure": "Fat Eco Serie"}},
        {"name": "fat_logi_linha", "type": "lineChart", "x": 660, "y": 545, "width": 600, "height": 130,
         "config": {"category": {"table": "ComparativoSerie", "column": "ano_mes"}, "measure": "Fat Logi Serie"}},
        {"name": "comb_eco_linha", "type": "lineChart", "x": 20, "y": 690, "width": 620, "height": 130,
         "config": {"category": {"table": "ComparativoSerie", "column": "ano_mes"}, "measure": "Comb Eco Serie"}},
        {"name": "comb_logi_linha", "type": "lineChart", "x": 660, "y": 690, "width": 600, "height": 130,
         "config": {"category": {"table": "ComparativoSerie", "column": "ano_mes"}, "measure": "Comb Logi Serie"}},
    ])

    b.add_page("Dashboard Energia Solar", [
        {"name": "paineis_card", "type": "card", "x": 20, "y": 20, "width": 180, "height": 90,
         "config": {"measure": "Qtd Paineis"}},
        {"name": "kwp_card", "type": "card", "x": 220, "y": 20, "width": 180, "height": 90,
         "config": {"measure": "Potencia Total kWp"}},
        {"name": "invest_card", "type": "card", "x": 420, "y": 20, "width": 220, "height": 90,
         "config": {"measure": "Investimento Solar"}},
        {"name": "cobertura_card", "type": "card", "x": 660, "y": 20, "width": 180, "height": 90,
         "config": {"measure": "Cobertura Solar Pct"}},
        {"name": "economia_card", "type": "card", "x": 860, "y": 20, "width": 200, "height": 90,
         "config": {"measure": "Economia Mensal Media"}},
        {"name": "roi_card", "type": "card", "x": 1080, "y": 20, "width": 180, "height": 90,
         "config": {"measure": "Semestre ROI"}},
        {"name": "bandeira_slicer", "type": "slicer", "x": 20, "y": 125, "width": 260, "height": 90,
         "config": {"column": {"table": "EnergiaSolarSemestre", "column": "bandeira_tarifaria"}}},
        {"name": "fixo_sem_linha", "type": "lineChart", "x": 20, "y": 230, "width": 620, "height": 200,
         "config": {"category": {"table": "EnergiaSolarSemestre", "column": "semestre_label"}, "measure": "Custo Fixo Medio Sem"}},
        {"name": "fixo_com_linha", "type": "lineChart", "x": 660, "y": 230, "width": 600, "height": 200,
         "config": {"category": {"table": "EnergiaSolarSemestre", "column": "semestre_label"}, "measure": "Custo Fixo Medio Com"}},
        {"name": "mensal_sem_linha", "type": "lineChart", "x": 20, "y": 450, "width": 620, "height": 200,
         "config": {"category": {"table": "EnergiaSolarSemestre", "column": "semestre_label"}, "measure": "Custo Semestral Sem Painel"}},
        {"name": "mensal_com_linha", "type": "lineChart", "x": 660, "y": 450, "width": 600, "height": 200,
         "config": {"category": {"table": "EnergiaSolarSemestre", "column": "semestre_label"}, "measure": "Custo Semestral Com Painel"}},
        {"name": "acum_sem_linha", "type": "lineChart", "x": 20, "y": 670, "width": 620, "height": 200,
         "config": {"category": {"table": "EnergiaSolarSemestre", "column": "semestre_label"}, "measure": "Acumulado Sem Painel"}},
        {"name": "acum_com_linha", "type": "lineChart", "x": 660, "y": 670, "width": 600, "height": 200,
         "config": {"category": {"table": "EnergiaSolarSemestre", "column": "semestre_label"}, "measure": "Acumulado Com Painel"}},
        {"name": "economia_acum_linha", "type": "lineChart", "x": 20, "y": 890, "width": 1240, "height": 180,
         "config": {"category": {"table": "EnergiaSolarSemestre", "column": "semestre_label"}, "measure": "Economia Acumulada"}},
    ])

    b.add_page("Dashboard ROI por Real", [
        {"name": "categoria_roi_slicer", "type": "slicer", "x": 20, "y": 20, "width": 280, "height": 90,
         "config": {"column": {"table": "RoiInvestimento", "column": "categoria"}}},
        {"name": "reais_frota_card", "type": "card", "x": 320, "y": 20, "width": 220, "height": 90,
         "config": {"measure": "Reais por Real Frota"}},
        {"name": "reais_solar_card", "type": "card", "x": 560, "y": 20, "width": 220, "height": 90,
         "config": {"measure": "Reais por Real Solar"}},
        {"name": "co2_frota_card", "type": "card", "x": 800, "y": 20, "width": 220, "height": 90,
         "config": {"measure": "CO2 kg por Real Frota"}},
        {"name": "co2_solar_card", "type": "card", "x": 1040, "y": 20, "width": 220, "height": 90,
         "config": {"measure": "CO2 kg por Real Solar"}},
        {"name": "inv_total_card", "type": "card", "x": 20, "y": 125, "width": 240, "height": 85,
         "config": {"measure": "Investimento Total EcoLogix"}},
        {"name": "eco_total_card", "type": "card", "x": 280, "y": 125, "width": 240, "height": 85,
         "config": {"measure": "Economia Operacional Anual"}},
        {"name": "co2_total_card", "type": "card", "x": 540, "y": 125, "width": 240, "height": 85,
         "config": {"measure": "CO2 Evitado Total Anual"}},
        {"name": "payback_card", "type": "card", "x": 800, "y": 125, "width": 200, "height": 85,
         "config": {"measure": "Payback Anos Consolidado"}},
        {"name": "roi_pct_card", "type": "card", "x": 1020, "y": 125, "width": 240, "height": 85,
         "config": {"measure": "ROI Anual Pct Consolidado"}},
        {"name": "co2_t_real_card", "type": "card", "x": 1280, "y": 125, "width": 220, "height": 85,
         "config": {"measure": "CO2 t por Real"}},
        {"name": "inv_frota_card", "type": "card", "x": 20, "y": 230, "width": 240, "height": 85,
         "config": {"measure": "Investimento Frota"}},
        {"name": "inv_solar_card", "type": "card", "x": 280, "y": 230, "width": 240, "height": 85,
         "config": {"measure": "Investimento Solar ROI"}},
        {"name": "eco_frota_card", "type": "card", "x": 540, "y": 230, "width": 240, "height": 85,
         "config": {"measure": "Economia Anual Frota"}},
        {"name": "eco_solar_card", "type": "card", "x": 800, "y": 230, "width": 240, "height": 85,
         "config": {"measure": "Economia Anual Solar"}},
        {"name": "reais_bar", "type": "clusteredBarChart", "x": 20, "y": 335, "width": 600, "height": 240,
         "config": {"category": {"table": "RoiInvestimento", "column": "categoria"}, "measure": "Reais por Real Investido"}},
        {"name": "co2_bar", "type": "clusteredBarChart", "x": 640, "y": 335, "width": 620, "height": 240,
         "config": {"category": {"table": "RoiInvestimento", "column": "categoria"}, "measure": "CO2 t por Real"}},
        {"name": "eco_acum_frota_linha", "type": "lineChart", "x": 20, "y": 595, "width": 620, "height": 260,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Economia Acum Frota"}},
        {"name": "eco_acum_solar_linha", "type": "lineChart", "x": 660, "y": 595, "width": 600, "height": 260,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Economia Acum Solar"}},
        {"name": "eco_acum_total_linha", "type": "lineChart", "x": 20, "y": 875, "width": 1240, "height": 200,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "Economia Acum Total"}},
        {"name": "eco_mensal_col", "type": "clusteredColumnChart", "x": 20, "y": 1095, "width": 620, "height": 220,
         "config": {"category": {"table": "RoiInvestimentoMensal", "column": "categoria"}, "measure": "Economia Mensal ROI"}},
        {"name": "co2_mensal_col", "type": "clusteredColumnChart", "x": 660, "y": 1095, "width": 600, "height": 220,
         "config": {"category": {"table": "RoiInvestimentoMensal", "column": "categoria"}, "measure": "CO2 Evitado Mensal kg"}},
        {"name": "co2_acum_frota_linha", "type": "lineChart", "x": 20, "y": 1335, "width": 620, "height": 180,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "CO2 Acum Frota kg"}},
        {"name": "co2_acum_solar_linha", "type": "lineChart", "x": 660, "y": 1335, "width": 600, "height": 180,
         "config": {"category": {"table": "Calendario", "column": "ano_mes"}, "measure": "CO2 Acum Solar kg"}},
    ])

    b.add_page("Simulador de Investimento", [
        {"name": "input_slicer", "type": "slicer", "x": 20, "y": 20, "width": 420, "height": 120,
         "config": {"column": {"table": "SimuladorInput", "column": "rotulo"}}},
        {"name": "valor_input_card", "type": "card", "x": 460, "y": 20, "width": 280, "height": 120,
         "config": {"measure": "Valor Investimento Selecionado"}},
        {"name": "co2_sim_card", "type": "card", "x": 20, "y": 160, "width": 360, "height": 140,
         "config": {"measure": "CO2 Evitado Simulado (kg)"}},
        {"name": "eco_sim_card", "type": "card", "x": 400, "y": 160, "width": 360, "height": 140,
         "config": {"measure": "Economia Simulada (R$)"}},
        {"name": "co2_t_sim_card", "type": "card", "x": 780, "y": 160, "width": 300, "height": 140,
         "config": {"measure": "CO2 Evitado Simulado (t)"}},
        {"name": "taxa_co2_card", "type": "card", "x": 20, "y": 320, "width": 300, "height": 100,
         "config": {"measure": "Taxa CO2 kg por Real"}},
        {"name": "taxa_eco_card", "type": "card", "x": 340, "y": 320, "width": 300, "height": 100,
         "config": {"measure": "Taxa Economia por Real"}},
        {"name": "simulador_bar", "type": "clusteredColumnChart", "x": 20, "y": 440, "width": 600, "height": 280,
         "config": {"category": {"table": "SimuladorInput", "column": "rotulo"}, "measure": "CO2 Evitado Simulado (kg)"}},
        {"name": "simulador_eco_bar", "type": "clusteredColumnChart", "x": 640, "y": 440, "width": 600, "height": 280,
         "config": {"category": {"table": "SimuladorInput", "column": "rotulo"}, "measure": "Economia Simulada (R$)"}},
    ])

    out = os.path.join(BASE, "EcoLogix_Dashboard.pbix")
    b.save(out)
    print(f"Arquivo criado: {out}")
    print("Abra no Power BI Desktop. 7 paginas, 13 tabelas, 56 medidas, 71 visuais.")


if __name__ == "__main__":
    main()

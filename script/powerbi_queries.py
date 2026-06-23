"""Consultas Power Query compartilhadas entre .pbit e .pbix."""
from __future__ import annotations

from pathlib import Path

MES_LIST = '{"Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"}'

TABLES = {
    "Calendario": {
        "csv": "calendario.csv",
        "periodo_id": False,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"ano_mes", Text.Type}, {"ordem", Int64.Type}',
    },
    "EntregasMensal": {
        "csv": "entregas_mensal.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"total_entregas", Int64.Type}, {"entregas_sucesso_1a_tentativa", Int64.Type}, {"taxa_reentrega_pct", Number.Type}, {"tempo_medio_entrega_min", Int64.Type}, {"produtividade_entregador_dia", Int64.Type}, {"distancia_media_km", Number.Type}, {"custo_medio_entrega_brl", Number.Type}, {"custo_reentrega_brl", Number.Type}, {"margem_lucro_entrega_brl", Number.Type}',
    },
    "EntregasRegional": {
        "csv": "entregas_regional.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"regiao", Text.Type}, {"total_entregas", Int64.Type}, {"taxa_sucesso_1a_tentativa_pct", Int64.Type}, {"tempo_medio_entrega_min", Int64.Type}, {"produtividade_entregador_dia", Int64.Type}, {"taxa_reentrega_pct", Number.Type}',
    },
    "FinanceiroMensal": {
        "csv": "financeiro_mensal.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"receita_total_brl", Int64.Type}, {"custo_operacional_brl", Int64.Type}, {"margem_lucro_operacional_pct", Number.Type}, {"custo_medio_entrega_brl", Number.Type}, {"custo_reentrega_total_brl", Int64.Type}, {"margem_lucro_entrega_brl", Number.Type}, {"custo_energia_rota_brl", Number.Type}',
    },
    "SustentabilidadeMensal": {
        "csv": "sustentabilidade_mensal.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"co2_evitado_toneladas", Number.Type}, {"consumo_kwh_km", Number.Type}, {"frota_eletrica_pct", Int64.Type}, {"modais_sustentaveis_pct", Int64.Type}, {"custo_energia_rota_brl", Number.Type}, {"emissao_co2_por_entrega_g", Int64.Type}',
    },
    "ClientesMensal": {
        "csv": "clientes_mensal.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"nps", Int64.Type}, {"avaliacao_media", Number.Type}, {"taxa_reclamacoes_pct", Number.Type}, {"entregas_avaliadas", Int64.Type}, {"clientes_ativos", Int64.Type}',
    },
    "ComparativoEmpresas": {
        "csv": "comparativo_empresas_mensal.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"empresa", Text.Type}, {"tipo_frota", Text.Type}, {"frota_veiculos", Int64.Type}, {"km_mes_frota", Int64.Type}, {"bandeira_tarifaria", Text.Type}, {"tarifa_kwh", Number.Type}, {"kwh_consumo_mes", Int64.Type}, {"faturamento_brl", Int64.Type}, {"custo_combustivel_brl", Int64.Type}, {"custo_manutencao_brl", Int64.Type}, {"emissao_co2_toneladas", Number.Type}, {"total_entregas", Int64.Type}, {"margem_operacional_pct", Number.Type}',
    },
    "ComparativoSerie": {
        "csv": "comparativo_serie.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"ano_mes", Text.Type}, {"ordem", Int64.Type}, {"faturamento_ecologix", Int64.Type}, {"faturamento_logitrans", Int64.Type}, {"combustivel_ecologix", Int64.Type}, {"combustivel_logitrans", Int64.Type}, {"manutencao_ecologix", Int64.Type}, {"manutencao_logitrans", Int64.Type}, {"co2_ecologix", Number.Type}, {"co2_logitrans", Number.Type}',
    },
    "CalendarioSemestre": {
        "csv": "calendario_semestre.csv",
        "periodo_id": False,
        "types": '{"semestre_ordem", Int64.Type}, {"semestre_id", Int64.Type}, {"semestre_label", Text.Type}, {"ano", Int64.Type}, {"semestre", Int64.Type}',
    },
    "EnergiaSolarSemestre": {
        "csv": "energia_solar_semestral_wide.csv",
        "periodo_id": False,
        "types": '{"semestre_ordem", Int64.Type}, {"semestre_id", Int64.Type}, {"semestre_label", Text.Type}, {"ano", Int64.Type}, {"semestre", Int64.Type}, {"bandeira_tarifaria", Text.Type}, {"tarifa_media_kwh", Number.Type}, {"custo_semestral_sem", Int64.Type}, {"custo_semestral_com", Int64.Type}, {"custo_fixo_medio_sem", Int64.Type}, {"custo_fixo_medio_com", Int64.Type}, {"custo_acumulado_sem", Int64.Type}, {"custo_acumulado_com", Int64.Type}, {"economia_semestral", Int64.Type}, {"economia_acumulada", Int64.Type}, {"roi_atingido", Int64.Type}',
    },
    "PaineisSolaresConfig": {
        "csv": "paineis_solares_config.csv",
        "periodo_id": False,
        "types": '{"frota_veiculos", Int64.Type}, {"km_dia_veiculo", Int64.Type}, {"qtd_paineis", Int64.Type}, {"potencia_painel_w", Int64.Type}, {"potencia_total_kwp", Number.Type}, {"kwh_dia_por_painel", Number.Type}, {"kwh_geracao_solar_mes", Int64.Type}, {"kwh_mes_frota", Int64.Type}, {"custo_instalacao_brl", Int64.Type}, {"cobertura_solar_pct", Int64.Type}, {"economia_mensal_media_brl", Int64.Type}, {"mes_roi", Int64.Type}, {"semestre_roi", Int64.Type}',
    },
    "Empresas": {
        "csv": "empresas.csv",
        "periodo_id": False,
        "types": '{"empresa_id", Int64.Type}, {"empresa", Text.Type}, {"tipo_frota", Text.Type}, {"cidade_sede", Text.Type}, {"frota_veiculos", Int64.Type}, {"ano_fundacao", Int64.Type}, {"descricao", Text.Type}',
    },
    "RoiInvestimento": {
        "csv": "roi_investimento.csv",
        "periodo_id": False,
        "types": '{"categoria_id", Int64.Type}, {"categoria", Text.Type}, {"tipo_tecnologia", Text.Type}, {"referencia_convencional", Text.Type}, {"investimento_brl", Int64.Type}, {"economia_anual_brl", Int64.Type}, {"co2_evitado_anual_t", Number.Type}, {"reais_por_real_investido", Number.Type}, {"co2_kg_por_real", Number.Type}',
    },
    "RoiInvestimentoMensal": {
        "csv": "roi_investimento_mensal.csv",
        "periodo_id": True,
        "types": '{"periodo_id", Int64.Type}, {"mes", Text.Type}, {"ano", Int64.Type}, {"categoria", Text.Type}, {"economia_mensal_brl", Int64.Type}, {"co2_evitado_mensal_kg", Number.Type}, {"economia_acumulada_brl", Int64.Type}, {"co2_evitado_acumulado_kg", Number.Type}, {"investimento_brl", Int64.Type}',
    },
}


def csv_path_expr(data_folder: str | Path, csv_name: str, use_parameter: bool) -> str:
    if use_parameter:
        return f'DataFolderPath & "\\{csv_name}"'
    full_path = str((Path(data_folder) / csv_name).resolve()).replace("/", "\\")
    return f'"{full_path.replace("\\", "\\\\")}"'


def build_m_query(table_name: str, data_folder: str | Path, use_parameter: bool = False) -> str:
    cfg = TABLES[table_name]
    path_expr = csv_path_expr(data_folder, cfg["csv"], use_parameter)
    lines = [
        "let",
        f"    Source = Csv.Document(File.Contents({path_expr}), [Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.None]),",
        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
    ]
    input_step = "PromotedHeaders"
    if cfg["periodo_id"]:
        lines.append(
            "    WithPeriodo = if List.Contains(Table.ColumnNames(PromotedHeaders), \"periodo_id\") "
            "then PromotedHeaders else Table.AddColumn(PromotedHeaders, \"periodo_id\", "
            f"each Number.From([ano]) * 100 + List.PositionOf({MES_LIST}, [mes]) + 1, Int64.Type),"
        )
        input_step = "WithPeriodo"
    lines.extend(
        [
            f"    TypedColumns = Table.TransformColumnTypes({input_step}, {{{cfg['types']}}})",
            "in",
            "    TypedColumns",
        ]
    )
    return "\n".join(lines)


def build_m_lines(table_name: str, data_folder: str | Path, use_parameter: bool = False) -> list[str]:
    return build_m_query(table_name, data_folder, use_parameter).split("\n")

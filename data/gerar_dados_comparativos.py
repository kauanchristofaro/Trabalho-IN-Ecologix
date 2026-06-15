"""Gera dados comparativos (20 veículos) e projeção de ROI dos painéis solares."""
import csv
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# --- Parâmetros da frota (ambas as empresas) ---
FROTA_VEICULOS = 20
KM_DIA_VEICULO = 120
DIAS_UTEIS_MES = 22

# --- Parâmetros energéticos EcoLogix ---
KWH_KM_INICIAL = 0.22
KWH_KM_FINAL = 0.16
TARIFA_BASE_KWH = 0.82
FATOR_CO2_KWH = 0.08

# --- Bandeiras tarifárias ANEEL (adicional R$/kWh sobre tarifa base) ---
BANDEIRAS_CICLO = [
    ("Verde", 0.0),
    ("Amarela", 0.01885),
    ("Amarela", 0.01885),
    ("Vermelha P1", 0.04463),
    ("Vermelha P1", 0.04463),
    ("Vermelha P2", 0.07877),
    ("Vermelha P2", 0.07877),
    ("Vermelha P1", 0.04463),
    ("Amarela", 0.01885),
    ("Verde", 0.0),
    ("Verde", 0.0),
    ("Amarela", 0.01885),
]

# --- Parâmetros LogiTrans (diesel) ---
CONSUMO_DIESEL_KM = 0.118
PRECO_DIESEL = 6.20
FATOR_CO2_DIESEL_KG_KM = 0.185

# --- Manutenção mensal por veículo ---
MANUT_ELETRICO_VEIC_MES = 590
MANUT_DIESEL_VEIC_MES = 1130

# --- Painéis solares (fixos conforme solicitado) ---
QTD_PAINEIS = 100
POTENCIA_PAINEL_W = 550
HORAS_SOL_PICO = 4.5
CUSTO_INSTALACAO = 250_000
CUSTO_OM_MENSAL = 1200


def read_csv(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name, fieldnames, rows):
    with open(os.path.join(BASE, name), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bandeira_mes(indice_mes):
    nome, adicional = BANDEIRAS_CICLO[indice_mes % 12]
    return nome, round(TARIFA_BASE_KWH + adicional, 5)


def kwh_km_mes(indice_mes):
    progresso = min(indice_mes, 11) / 11
    return KWH_KM_INICIAL - (KWH_KM_INICIAL - KWH_KM_FINAL) * progresso


def km_mes_frota(indice_mes):
    fator_eficiencia = 1 - min(indice_mes, 11) * 0.004
    return round(FROTA_VEICULOS * KM_DIA_VEICULO * DIAS_UTEIS_MES * fator_eficiencia)


def kwh_mes_frota(indice_mes):
    return round(km_mes_frota(indice_mes) * kwh_km_mes(indice_mes))


def kwh_geracao_solar_mes():
    kwh_dia_painel = (POTENCIA_PAINEL_W / 1000) * HORAS_SOL_PICO
    return round(QTD_PAINEIS * kwh_dia_painel * DIAS_UTEIS_MES)


def gerar_comparativo():
    financeiro = {r["mes"]: r for r in read_csv("financeiro_mensal.csv")}
    entregas = {r["mes"]: r for r in read_csv("entregas_mensal.csv")}

    comparativo = []

    for i, mes in enumerate(MESES):
        fin = financeiro[mes]
        ent = entregas[mes]
        ano = fin["ano"]
        km_total = km_mes_frota(i)
        kwh_km = kwh_km_mes(i)
        kwh_consumo = round(km_total * kwh_km)
        bandeira, tarifa = bandeira_mes(i)
        distancia = float(ent["distancia_media_km"])
        total_entregas = round(km_total / distancia)

        faturamento_eco = round(total_entregas * float(fin["receita_total_brl"]) / int(ent["total_entregas"]))
        margem_eco = float(fin["margem_lucro_operacional_pct"])

        custo_energia_eco = round(kwh_consumo * tarifa)
        custo_manutencao_eco = FROTA_VEICULOS * MANUT_ELETRICO_VEIC_MES
        emissao_co2_eco = round(kwh_consumo * FATOR_CO2_KWH / 1000, 2)

        faturamento_logi = round(faturamento_eco * 0.95)
        margem_logi = round(margem_eco - 4.3, 1)
        custo_combustivel_logi = round(km_total * CONSUMO_DIESEL_KM * PRECO_DIESEL)
        custo_manutencao_logi = FROTA_VEICULOS * MANUT_DIESEL_VEIC_MES
        emissao_co2_logi = round(km_total * FATOR_CO2_DIESEL_KG_KM / 1000, 2)

        for empresa, tipo, fat, comb, manut, co2, margem in [
            ("EcoLogix Solutions", "Eletrica", faturamento_eco, custo_energia_eco,
             custo_manutencao_eco, emissao_co2_eco, margem_eco),
            ("LogiTrans Express", "Convencional", faturamento_logi, custo_combustivel_logi,
             custo_manutencao_logi, emissao_co2_logi, margem_logi),
        ]:
            comparativo.append({
                "mes": mes,
                "ano": ano,
                "empresa": empresa,
                "tipo_frota": tipo,
                "frota_veiculos": FROTA_VEICULOS,
                "km_mes_frota": km_total,
                "bandeira_tarifaria": bandeira,
                "tarifa_kwh": tarifa,
                "kwh_consumo_mes": kwh_consumo,
                "faturamento_brl": fat,
                "custo_combustivel_brl": comb,
                "custo_manutencao_brl": manut,
                "emissao_co2_toneladas": co2,
                "total_entregas": total_entregas,
                "margem_operacional_pct": margem,
            })

    fields = [
        "mes", "ano", "empresa", "tipo_frota", "frota_veiculos", "km_mes_frota",
        "bandeira_tarifaria", "tarifa_kwh", "kwh_consumo_mes",
        "faturamento_brl", "custo_combustivel_brl", "custo_manutencao_brl",
        "emissao_co2_toneladas", "total_entregas", "margem_operacional_pct",
    ]
    write_csv("comparativo_empresas_mensal.csv", fields, comparativo)
    print(f"Gerado: comparativo_empresas_mensal.csv ({len(comparativo)} linhas, frota={FROTA_VEICULOS})")
    gerar_comparativo_serie(comparativo)


def gerar_comparativo_serie(comparativo):
    """Tabela wide (1 linha/mês) para gráficos de linha sem CALCULATE."""
    meses_ordem = {m: i + 1 for i, m in enumerate(MESES)}
    por_mes = {}
    for r in comparativo:
        chave = (r["mes"], r["ano"])
        if chave not in por_mes:
            pid = int(r["ano"]) * 100 + meses_ordem[r["mes"]]
            por_mes[chave] = {
                "periodo_id": pid,
                "mes": r["mes"],
                "ano": r["ano"],
                "ano_mes": f"{r['ano']}-{meses_ordem[r['mes']]:02d}",
                "ordem": meses_ordem[r["mes"]],
            }
        prefix = "ecologix" if r["empresa"] == "EcoLogix Solutions" else "logitrans"
        por_mes[chave][f"faturamento_{prefix}"] = r["faturamento_brl"]
        por_mes[chave][f"combustivel_{prefix}"] = r["custo_combustivel_brl"]
        por_mes[chave][f"manutencao_{prefix}"] = r["custo_manutencao_brl"]
        por_mes[chave][f"co2_{prefix}"] = r["emissao_co2_toneladas"]

    serie = [por_mes[k] for k in sorted(por_mes, key=lambda x: por_mes[x]["periodo_id"])]
    fields = [
        "periodo_id", "mes", "ano", "ano_mes", "ordem",
        "faturamento_ecologix", "faturamento_logitrans",
        "combustivel_ecologix", "combustivel_logitrans",
        "manutencao_ecologix", "manutencao_logitrans",
        "co2_ecologix", "co2_logitrans",
    ]
    write_csv("comparativo_serie.csv", fields, serie)
    print(f"Gerado: comparativo_serie.csv ({len(serie)} linhas)")


def semestre_info(mes_idx, ano):
    semestre = 1 if mes_idx < 6 else 2
    return semestre, f"{ano}-S{semestre}", ano * 10 + semestre


def gerar_energia_solar_semestral(energia_mensal):
    """Agrega dados mensais em semestres para o dashboard."""
    buckets = {}
    for r in energia_mensal:
        mes_idx = MESES.index(r["mes"])
        sem, label, sid = semestre_info(mes_idx, r["ano"])
        chave = (r["ano"], sem, r["cenario"])
        if chave not in buckets:
            buckets[chave] = {
                "semestre_id": sid,
                "semestre_label": label,
                "ano": r["ano"],
                "semestre": sem,
                "cenario": r["cenario"],
                "meses": [],
            }
        buckets[chave]["meses"].append(r)

    semestral = []
    semestre_ordem = 0
    labels_ordenados = sorted({b["semestre_label"] for b in buckets.values()})

    for label in labels_ordenados:
        semestre_ordem += 1
        for cenario in ("Sem Painel", "Com Painel"):
            chave = next(
                (k for k, b in buckets.items() if b["semestre_label"] == label and b["cenario"] == cenario),
                None,
            )
            if not chave:
                continue
            meses = sorted(buckets[chave]["meses"], key=lambda x: x["mes_numero"])
            custo_sem = sum(m["custo_mensal_brl"] for m in meses)
            fixos = [m["custo_fixo_mensal_brl"] for m in meses]
            ultimo = meses[-1]
            bandeiras = [m["bandeira_tarifaria"] for m in meses]
            bandeira_pred = max(set(bandeiras), key=bandeiras.count)
            semestral.append({
                "semestre_ordem": semestre_ordem,
                "semestre_id": buckets[chave]["semestre_id"],
                "semestre_label": label,
                "ano": buckets[chave]["ano"],
                "semestre": buckets[chave]["semestre"],
                "bandeira_tarifaria": bandeira_pred,
                "tarifa_media_kwh": round(sum(m["tarifa_kwh"] for m in meses) / len(meses), 5),
                "cenario": cenario,
                "custo_semestral_brl": custo_sem,
                "custo_fixo_medio_brl": round(sum(fixos) / len(fixos)),
                "custo_acumulado_brl": ultimo["custo_acumulado_brl"],
                "economia_semestral_brl": sum(m["economia_mensal_brl"] for m in meses),
                "economia_acumulada_brl": ultimo["economia_acumulada_brl"],
                "roi_atingido": max(m["roi_atingido"] for m in meses),
            })

    fields = [
        "semestre_ordem", "semestre_id", "semestre_label", "ano", "semestre",
        "bandeira_tarifaria", "tarifa_media_kwh", "cenario",
        "custo_semestral_brl", "custo_fixo_medio_brl", "custo_acumulado_brl",
        "economia_semestral_brl", "economia_acumulada_brl", "roi_atingido",
    ]
    write_csv("energia_solar_semestral.csv", fields, semestral)

    wide_map = {}
    for r in semestral:
        label = r["semestre_label"]
        if label not in wide_map:
            wide_map[label] = {
                "semestre_ordem": r["semestre_ordem"],
                "semestre_id": r["semestre_id"],
                "semestre_label": label,
                "ano": r["ano"],
                "semestre": r["semestre"],
                "bandeira_tarifaria": r["bandeira_tarifaria"],
                "tarifa_media_kwh": r["tarifa_media_kwh"],
            }
        sufixo = "sem" if r["cenario"] == "Sem Painel" else "com"
        wide_map[label][f"custo_semestral_{sufixo}"] = r["custo_semestral_brl"]
        wide_map[label][f"custo_fixo_medio_{sufixo}"] = r["custo_fixo_medio_brl"]
        wide_map[label][f"custo_acumulado_{sufixo}"] = r["custo_acumulado_brl"]
        if sufixo == "com":
            wide_map[label]["economia_semestral"] = r["economia_semestral_brl"]
            wide_map[label]["economia_acumulada"] = r["economia_acumulada_brl"]
            wide_map[label]["roi_atingido"] = r["roi_atingido"]

    wide_rows = [wide_map[k] for k in sorted(wide_map, key=lambda x: wide_map[x]["semestre_ordem"])]
    wide_fields = [
        "semestre_ordem", "semestre_id", "semestre_label", "ano", "semestre",
        "bandeira_tarifaria", "tarifa_media_kwh",
        "custo_semestral_sem", "custo_semestral_com",
        "custo_fixo_medio_sem", "custo_fixo_medio_com",
        "custo_acumulado_sem", "custo_acumulado_com",
        "economia_semestral", "economia_acumulada", "roi_atingido",
    ]
    write_csv("energia_solar_semestral_wide.csv", wide_fields, wide_rows)

    roi_sem = next((r["semestre_ordem"] for r in semestral if r["roi_atingido"] == 1), 0)
    print(f"Gerado: energia_solar_semestral.csv ({len(semestral)} linhas, ROI no semestre {roi_sem})")
    return roi_sem


def gerar_energia_solar():
    kwh_dia_painel = round((POTENCIA_PAINEL_W / 1000) * HORAS_SOL_PICO, 2)
    potencia_kwp = round(QTD_PAINEIS * POTENCIA_PAINEL_W / 1000, 1)
    kwh_solar_mes = kwh_geracao_solar_mes()
    kwh_frota_inicial = kwh_mes_frota(0)
    cobertura_inicial = min(100, round(kwh_solar_mes / kwh_frota_inicial * 100)) if kwh_frota_inicial else 0

    config = [{
        "frota_veiculos": FROTA_VEICULOS,
        "km_dia_veiculo": KM_DIA_VEICULO,
        "qtd_paineis": QTD_PAINEIS,
        "potencia_painel_w": POTENCIA_PAINEL_W,
        "potencia_total_kwp": potencia_kwp,
        "kwh_dia_por_painel": kwh_dia_painel,
        "kwh_geracao_solar_mes": kwh_solar_mes,
        "custo_instalacao_brl": CUSTO_INSTALACAO,
        "cobertura_solar_pct": cobertura_inicial,
        "economia_mensal_media_brl": 0,
        "mes_roi": 0,
        "semestre_roi": 0,
    }]

    energia = []
    acum_sem = 0
    acum_com = 0
    economia_acum = 0
    roi_atingido = 0
    economias_mensais = []

    m = 0
    while True:
        m += 1
        mes_idx = (m - 1) % 12
        ano = 2025 + (m - 1) // 12
        mes_nome = MESES[mes_idx]
        periodo_label = f"M{m:02d} ({mes_nome}/{str(ano)[2:]})"

        bandeira, tarifa = bandeira_mes(mes_idx)
        kwh_frota = kwh_mes_frota(min(m - 1, 11))
        kwh_rede = max(0, kwh_frota - kwh_solar_mes)

        custo_sem = round(kwh_frota * tarifa)
        custo_fixo_com = CUSTO_OM_MENSAL + round(kwh_rede * tarifa)
        economia_mes = custo_sem - custo_fixo_com
        economias_mensais.append(economia_mes)

        acum_sem += custo_sem
        if m == 1:
            custo_mes_com = CUSTO_INSTALACAO + custo_fixo_com
        else:
            custo_mes_com = custo_fixo_com
        acum_com += custo_mes_com

        if m > 1:
            economia_acum += economia_mes
        if economia_acum >= CUSTO_INSTALACAO and roi_atingido == 0:
            roi_atingido = m

        for cenario, custo_mes, custo_acum, fixo in [
            ("Sem Painel", custo_sem, acum_sem, custo_sem),
            ("Com Painel", custo_mes_com, acum_com, custo_fixo_com),
        ]:
            energia.append({
                "mes_numero": m,
                "periodo_label": periodo_label,
                "mes": mes_nome,
                "ano": ano,
                "bandeira_tarifaria": bandeira,
                "tarifa_kwh": tarifa,
                "kwh_consumo_mes": kwh_frota,
                "kwh_geracao_solar_mes": kwh_solar_mes,
                "kwh_rede_mes": kwh_rede,
                "cenario": cenario,
                "custo_mensal_brl": custo_mes,
                "custo_fixo_mensal_brl": fixo,
                "custo_acumulado_brl": custo_acum,
                "economia_mensal_brl": economia_mes if cenario == "Com Painel" else 0,
                "economia_acumulada_brl": economia_acum if cenario == "Com Painel" else 0,
                "roi_atingido": 1 if m == roi_atingido and cenario == "Com Painel" else 0,
            })

        if roi_atingido and m >= roi_atingido + 2:
            break
        if m >= 120:
            break

    config[0]["economia_mensal_media_brl"] = round(sum(economias_mensais) / len(economias_mensais))
    config[0]["mes_roi"] = roi_atingido
    config[0]["kwh_mes_frota"] = kwh_frota_inicial
    config[0]["semestre_roi"] = gerar_energia_solar_semestral(energia)

    fields_config = list(config[0].keys())
    write_csv("paineis_solares_config.csv", fields_config, config)

    fields = [
        "mes_numero", "periodo_label", "mes", "ano", "bandeira_tarifaria", "tarifa_kwh",
        "kwh_consumo_mes", "kwh_geracao_solar_mes", "kwh_rede_mes", "cenario",
        "custo_mensal_brl", "custo_fixo_mensal_brl", "custo_acumulado_brl",
        "economia_mensal_brl", "economia_acumulada_brl", "roi_atingido",
    ]
    write_csv("energia_solar_mensal.csv", fields, energia)

    print(f"Gerado: paineis_solares_config.csv (100 placas, R$ {CUSTO_INSTALACAO:,})")
    print(f"Gerado: energia_solar_mensal.csv ({len(energia)} linhas, ROI no mes {roi_atingido})")
    print(f"  Geração solar: {kwh_solar_mes} kWh/mes | Cobertura: {cobertura_inicial}%")
    print(f"  Economia mensal média: R$ {config[0]['economia_mensal_media_brl']:,}")


def main():
    gerar_comparativo()
    gerar_energia_solar()


if __name__ == "__main__":
    main()

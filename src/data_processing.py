import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def get_filtered_data_by_range(df: pd.DataFrame, range_type: str) -> pd.DataFrame:
    """Filtra o DataFrame pelo período selecionado."""
    if df.empty:
        return df

    hoje = datetime.now()
    ranges = {
        "1M": hoje - timedelta(days=30),
        "2M": hoje - timedelta(days=60),
        "3M": hoje - timedelta(days=90),
        "6M": hoje - timedelta(days=180),
        "YTD": datetime(hoje.year, 1, 1),
    }

    if range_type == "ALL" or range_type not in ranges:
        return df

    return df[df.index >= ranges[range_type]]


def _calcular_sar(df: pd.DataFrame, af_step: float = 0.02, af_max: float = 0.20) -> pd.Series:
    """
    Calcula o Parabolic SAR usando o algoritmo iterativo padrão de Wilder.
    Retorna uma Series com o mesmo índice do DataFrame.
    """
    highs = df["high"].values
    lows = df["low"].values
    n = len(highs)

    if n < 2:
        return pd.Series([np.nan] * n, index=df.index)

    sar = np.full(n, np.nan)
    # Inicializa: assume tendência de alta
    bull = True
    af = af_step
    ep = highs[0]          # Extreme Point
    sar[0] = lows[0]       # SAR inicial

    for i in range(1, n):
        prev_sar = sar[i - 1]

        if bull:
            # Tendência de alta: SAR sobe, abaixo do preço
            sar[i] = prev_sar + af * (ep - prev_sar)
            # SAR não pode estar acima das duas mínimas anteriores
            if i >= 2:
                sar[i] = min(sar[i], lows[i - 1], lows[i - 2])
            else:
                sar[i] = min(sar[i], lows[i - 1])

            if lows[i] < sar[i]:
                # Reversão: passa para tendência de baixa
                bull = False
                sar[i] = ep          # SAR vai para o EP anterior (máxima)
                ep = lows[i]
                af = af_step
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + af_step, af_max)
        else:
            # Tendência de baixa: SAR cai, acima do preço
            sar[i] = prev_sar + af * (ep - prev_sar)
            # SAR não pode estar abaixo das duas máximas anteriores
            if i >= 2:
                sar[i] = max(sar[i], highs[i - 1], highs[i - 2])
            else:
                sar[i] = max(sar[i], highs[i - 1])

            if highs[i] > sar[i]:
                # Reversão: passa para tendência de alta
                bull = True
                sar[i] = ep          # SAR vai para o EP anterior (mínima)
                ep = highs[i]
                af = af_step
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + af_step, af_max)

    return pd.Series(sar, index=df.index)


def calcular_indicadores(
    df: pd.DataFrame, indicadores: list
) -> pd.DataFrame:
    """
    Calcula indicadores técnicos no DataFrame OHLC completo.
    Deve ser chamado antes de aplicar filtro de período.
    """
    if df.empty:
        return df

    df = df.copy()

    if "SMA8" in indicadores:
        df["SMA8"] = df["close"].rolling(window=8, min_periods=1).mean()
    if "SMA20" in indicadores:
        df["SMA20"] = df["close"].rolling(window=20, min_periods=1).mean()
    if "SMA50" in indicadores:
        df["SMA50"] = df["close"].rolling(window=50, min_periods=1).mean()
    if "Bollinger Bands 8" in indicadores:
        rolling_mean = df["close"].rolling(window=8, min_periods=1).mean()
        rolling_std = df["close"].rolling(window=8, min_periods=1).std()
        df["BB_upper"] = rolling_mean + (rolling_std * 2)
        df["BB_mid"] = rolling_mean
        df["BB_lower"] = rolling_mean - (rolling_std * 2)
    if "SAR Parabólico" in indicadores:
        df["SAR"] = _calcular_sar(df)
        # Marca tendência: True = bull (SAR abaixo do close), False = bear
        df["SAR_bull"] = df["SAR"] < df["close"]

    return df


def calcular_vwap(df_product: pd.DataFrame, timeframe: str = "Diário") -> pd.Series:
    """
    Calcula o preço médio ponderado por volume (VWAP) agrupado pelo timeframe.
    Retorna Series com índice DatetimeIndex compatível com o resultado de build_ohlc.
    """
    if df_product.empty:
        return pd.Series(dtype=float)

    rule = TIMEFRAME_RESAMPLE.get(timeframe, "D")

    # Agrupa pelo mesmo período do resample para compatibilidade com o índice do OHLC
    grouped = df_product.resample(rule)
    vwap_dict = {}
    for periodo, grupo in grouped:
        total_qty = grupo["quantity"].sum()
        if total_qty > 0:
            vwap_dict[periodo] = (
                (grupo["unitPrice"] * grupo["quantity"]).sum() / total_qty
            )

    return pd.Series(vwap_dict)


# Mapeamento timeframe → regra de resample do pandas
TIMEFRAME_RESAMPLE = {
    "Diário":     "D",
    "Semanal":    "W",
    "Quinzenal":  "SM",   # semi-month: cortes em 1º e 15 de cada mês
    "Mensal":     "ME",   # month-end
}

# Formato de data exibido no eixo X de cada timeframe
TIMEFRAME_DATE_FMT = {
    "Diário":    "%d/%m",
    "Semanal":   "%d/%m",
    "Quinzenal": "%d/%m",
    "Mensal":    "%b/%y",
}


def build_ohlc(df_product: pd.DataFrame, timeframe: str = "Diário") -> pd.DataFrame:
    """
    Constrói DataFrame OHLC a partir dos trades de um produto.
    Remove períodos sem negociação.

    Timeframes disponíveis: Diário, Semanal, Quinzenal, Mensal.
    """
    if df_product.empty:
        return pd.DataFrame()

    rule = TIMEFRAME_RESAMPLE.get(timeframe, "D")
    df_ohlc = df_product["unitPrice"].resample(rule).ohlc()
    df_ohlc["volume"] = df_product.resample(rule)["quantity"].sum()
    return df_ohlc.dropna()


def criar_tabela_ohlc(
    df_ohlc: pd.DataFrame, vwap: pd.Series, timeframe: str = "Diário"
) -> pd.DataFrame:
    """
    Retorna tabela com OHLC, VWAP e volume para exibição.
    Mostra até 60 registros, do mais recente ao mais antigo.
    O formato da coluna Data se adapta ao timeframe.
    """
    if df_ohlc.empty:
        return pd.DataFrame()

    # Formato de data por timeframe
    date_fmt = {
        "Diário":    "%d/%m/%Y",
        "Semanal":   "Sem %d/%m/%Y",
        "Quinzenal": "%d/%m/%Y",
        "Mensal":    "%b/%Y",
    }.get(timeframe, "%d/%m/%Y")

    df_ultimos = df_ohlc.tail(60).iloc[::-1].copy()
    rows = []

    for idx, row in df_ultimos.iterrows():
        preco_medio = vwap.get(idx)
        if preco_medio is None or pd.isna(preco_medio):
            preco_medio = (
                row["open"] + row["high"] + row["low"] + row["close"]
            ) / 4

        rows.append(
            {
                "Data": idx.strftime(date_fmt),
                "Open": round(row["open"], 2),
                "High": round(row["high"], 2),
                "Low": round(row["low"], 2),
                "Close": round(row["close"], 2),
                "Pmédio": round(preco_medio, 2),
                "Vol (MWm)": int(row["volume"]) if not pd.isna(row["volume"]) else 0,
            }
        )

    return pd.DataFrame(rows)

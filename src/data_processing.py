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

    return df


def calcular_vwap(df_product: pd.DataFrame) -> pd.Series:
    """
    Calcula o preço médio ponderado por volume (VWAP) para cada dia.
    Retorna Series com índice DatetimeIndex (datas).
    """
    if df_product.empty:
        return pd.Series(dtype=float)

    df = df_product.copy()
    df["data"] = df.index.normalize()  # DatetimeIndex truncado ao dia

    vwap_dict = {}
    for data, grupo in df.groupby("data"):
        total_qty = grupo["quantity"].sum()
        if total_qty > 0:
            vwap_dict[data] = (grupo["unitPrice"] * grupo["quantity"]).sum() / total_qty

    return pd.Series(vwap_dict)


def build_ohlc(df_product: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói DataFrame OHLC diário a partir dos trades de um produto.
    Remove dias sem negociação.
    """
    if df_product.empty:
        return pd.DataFrame()

    df_ohlc = df_product["unitPrice"].resample("D").ohlc()
    df_ohlc["volume"] = df_product.resample("D")["quantity"].sum()
    return df_ohlc.dropna()


def criar_tabela_ohlc(
    df_ohlc: pd.DataFrame, vwap: pd.Series
) -> pd.DataFrame:
    """
    Retorna tabela com OHLC, VWAP e volume para exibição.
    Mostra até 60 registros, do mais recente ao mais antigo.
    """
    if df_ohlc.empty:
        return pd.DataFrame()

    df_ultimos = df_ohlc.tail(60).iloc[::-1].copy()
    rows = []

    for idx, row in df_ultimos.iterrows():
        # Busca VWAP pelo índice normalizado (datetime sem hora)
        data_key = idx.normalize()
        preco_medio = vwap.get(data_key)

        if preco_medio is None or pd.isna(preco_medio):
            preco_medio = (
                row["open"] + row["high"] + row["low"] + row["close"]
            ) / 4

        rows.append(
            {
                "Data": idx.strftime("%d/%m/%Y"),
                "Open": round(row["open"], 2),
                "High": round(row["high"], 2),
                "Low": round(row["low"], 2),
                "Close": round(row["close"], 2),
                "Pmédio": round(preco_medio, 2),
                "Vol (MWm)": int(row["volume"]) if not pd.isna(row["volume"]) else 0,
            }
        )

    return pd.DataFrame(rows)

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_processing import TIMEFRAME_DATE_FMT

COLORS_IND = {"SMA8": "#FB8E00", "SMA20": "#1E88E5", "SMA50": "#4CAF50"}


def _last_valid(series: pd.Series):
    """Retorna o último valor não-nulo de uma Series, ou None."""
    clean = series.dropna()
    return clean.iloc[-1] if not clean.empty else None


def plot_produto_com_volume(
    df_filtrado: pd.DataFrame,
    indicadores: list,
    timeframe: str = "Diário",
    height: int = 550,
) -> go.Figure:
    """
    Gráfico candlestick + volume em barras.
    Usa eixo categórico (apenas períodos com negociação).
    """
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados disponíveis", x=0.5, y=0.5, showarrow=False)
        return fig

    date_fmt = TIMEFRAME_DATE_FMT.get(timeframe, "%d/%m")
    datas_str = df_filtrado.index.strftime(date_fmt).tolist()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.8, 0.2],
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=datas_str,
            open=df_filtrado["open"],
            high=df_filtrado["high"],
            low=df_filtrado["low"],
            close=df_filtrado["close"],
            name="Preço",
            showlegend=False,
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1,
        col=1,
    )
    fig.update_layout(xaxis_rangeslider_visible=False)

    # Indicadores
    for ind in indicadores:
        if ind in ("SMA8", "SMA20", "SMA50") and ind in df_filtrado.columns:
            ultimo = _last_valid(df_filtrado[ind])
            label = f"<b>{ind}</b>: {ultimo:.1f}" if ultimo is not None else ind
            fig.add_trace(
                go.Scatter(
                    x=datas_str,
                    y=df_filtrado[ind],
                    mode="lines",
                    name=label,
                    line=dict(color=COLORS_IND.get(ind, "gray"), width=1.5),
                ),
                row=1,
                col=1,
            )

        elif ind == "Bollinger Bands 8" and "BB_upper" in df_filtrado.columns:
            ultimo_mid = _last_valid(df_filtrado["BB_mid"])

            fig.add_trace(
                go.Scatter(
                    x=datas_str,
                    y=df_filtrado["BB_upper"],
                    mode="lines",
                    name="BB Sup",
                    line=dict(color="rgba(255,99,71,0.5)", width=1, dash="dash"),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=datas_str,
                    y=df_filtrado["BB_mid"],
                    mode="lines",
                    name=f"<b>BB Mid</b>: {ultimo_mid:.1f}"
                    if ultimo_mid is not None
                    else "BB Mid",
                    line=dict(color="rgba(255,99,71,0.5)", width=1.5),
                    fill="tonexty",
                    fillcolor="rgba(255,99,71,0.1)",
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=datas_str,
                    y=df_filtrado["BB_lower"],
                    mode="lines",
                    name="BB Inf",
                    line=dict(color="rgba(255,99,71,0.5)", width=1, dash="dash"),
                    fill="tonexty",
                    fillcolor="rgba(255,99,71,0.1)",
                ),
                row=1,
                col=1,
            )

    # Volume
    if "volume" in df_filtrado.columns:
        colors_vol = [
            "#ef5350"
            if df_filtrado["close"].iloc[i] < df_filtrado["open"].iloc[i]
            else "#26a69a"
            for i in range(len(df_filtrado))
        ]
        fig.add_trace(
            go.Bar(
                x=datas_str,
                y=df_filtrado["volume"],
                name="Volume",
                marker_color=colors_vol,
                hovertemplate="<b>%{y:,.0f} MWm</b><extra></extra>",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        height=height,
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=30, r=30, t=25, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=17),
            itemsizing="constant",
        ),
    )
    fig.update_xaxes(type="category", tickangle=45, nticks=10, tickfont=dict(size=13))
    fig.update_yaxes(
        title_text="Preço (R$/MWh)", row=1, col=1, tickformat=".0f",
        title_font=dict(size=14)
    )
    fig.update_yaxes(
        title_text="Volume (MWm)", row=2, col=1, tickformat=",.0f",
        title_font=dict(size=14)
    )

    return fig


def plot_spread_area(
    df_produto1: pd.DataFrame,
    df_produto2: pd.DataFrame,
    nome1: str,
    nome2: str,
    timeframe: str = "Diário",
    height: int = 550,
) -> go.Figure:
    """
    Gráfico de spread (produto1.close - produto2.close) como área preenchida.
    Usa eixo categórico.
    """
    if df_produto1.empty or df_produto2.empty:
        fig = go.Figure()
        fig.add_annotation(text="Dados insuficientes", x=0.5, y=0.5, showarrow=False)
        return fig

    datas_comuns = df_produto1.index.intersection(df_produto2.index)
    if len(datas_comuns) == 0:
        fig = go.Figure()
        fig.add_annotation(text="Sem datas em comum", x=0.5, y=0.5, showarrow=False)
        return fig

    df_spread = pd.DataFrame(index=datas_comuns)

    if nome1 == nome2:
        df_spread["spread"] = 0.0
    else:
        df_spread["spread"] = (
            df_produto1.loc[datas_comuns, "close"]
            - df_produto2.loc[datas_comuns, "close"]
        )

    ultimo_spread = df_spread["spread"].iloc[-1]
    date_fmt = TIMEFRAME_DATE_FMT.get(timeframe, "%d/%m")
    datas_str = df_spread.index.strftime(date_fmt).tolist()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=datas_str,
            y=df_spread["spread"],
            mode="lines",
            fill="tozeroy",
            name="Spread",
            line=dict(color="#797979", width=2),
            fillcolor="rgba(117,117,117,0.2)",
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_annotation(
        x=datas_str[-1],
        y=ultimo_spread,
        text=f"R$ {ultimo_spread:.2f}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#797979",
        font=dict(size=13, color="#333"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#797979",
        borderwidth=1,
        borderpad=4,
        ax=20,
        ay=-30,
    )
    fig.update_layout(
        height=height,
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=30, r=30, t=25, b=20),
        showlegend=False,
    )
    fig.update_xaxes(type="category", tickangle=45, nticks=8, tickfont=dict(size=13))
    fig.update_yaxes(
        title_text="Spread (R$/MWh)", tickformat=".0f", title_font=dict(size=13)
    )
    return fig

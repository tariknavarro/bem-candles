import time
from threading import Thread

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.auth import show_login
from src.bbce_api import connect_bbce, refresh_deals
from src.charts import plot_produto_com_volume, plot_spread_area
from src.data_processing import (
    build_ohlc,
    calcular_indicadores,
    calcular_vwap,
    criar_tabela_ohlc,
    get_filtered_data_by_range,
)

# Carrega variáveis do .env em desenvolvimento local
load_dotenv()

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="BEM Energia Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    .main > div { padding-top: 0.5rem; }
    .block-container {
        padding-top: 1rem; padding-bottom: 0rem;
        padding-left: 1rem; padding-right: 1rem;
    }
    h1 {
        margin-top: 0rem !important;
        margin-bottom: 0.25rem !important;
        font-size: 1.8rem !important;
    }
    .update-info {
        text-align: center; color: #666;
        font-size: 0.75rem;
        margin-top: -0.25rem; margin-bottom: 0.25rem;
    }
    div[data-testid="stMultiSelect"] label { font-size: 1rem !important; }
    div[data-testid="stRadio"] label { font-size: 1rem !important; }
    div[data-testid="stSelectbox"] label {
        font-size: 1rem !important; font-weight: 400 !important;
        color: #495057 !important;
    }
    div[data-testid="column"] { padding: 0 0.25rem !important; }
    .stPlotlyChart { margin-bottom: 0.5rem !important; }
    .dataframe { font-size: 11px !important; }
    .dataframe th { background-color: #f8f9fa; font-weight: 600; padding: 0.25rem !important; }
    .dataframe td { padding: 0.2rem !important; }
    h3, .stMarkdown h3 { font-size: 0.9rem !important; margin: 0.25rem 0 !important; }
</style>
""",
    unsafe_allow_html=True,
)


# ==================== UTILITÁRIOS ====================
def _build_produtos(df: pd.DataFrame, tickers_validos: list) -> list:
    """Retorna lista de produtos ordenados por volume para o DataFrame fornecido."""
    if df.empty:
        return []
    volume_por_produto = (
        df.groupby("productId")["quantity"].sum().sort_values(ascending=False)
    )
    produtos = []
    for product_id in volume_por_produto.index:
        descricao = next(
            (t.get("description", "") for t in tickers_validos if t["id"] == product_id),
            None,
        )
        if descricao and descricao.strip():
            produtos.append(
                {
                    "id": product_id,
                    "description": descricao,
                    "volume": volume_por_produto[product_id],
                }
            )
    return produtos


# ==================== ATUALIZAÇÃO AUTOMÁTICA ====================
def _auto_refresh_thread():
    """Recarrega deals a cada 20 minutos em background."""
    while True:
        time.sleep(1200)
        refresh_deals()


# ==================== INTERFACE PRINCIPAL ====================
def main():
    # Inicialização de estados
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "logado_bbce" not in st.session_state:
        st.session_state.logado_bbce = False

    st.markdown(
        "<h1 style='text-align:center; margin:0.1rem 0;'>📊 BEM Energia Dashboard</h1>",
        unsafe_allow_html=True,
    )

    # --- Login do usuário ---
    if not st.session_state.autenticado:
        show_login()
        return

    # --- Conexão com a BBCE ---
    if not st.session_state.logado_bbce:
        st.info("Usuário autenticado. Conectando à BBCE e carregando dados...")
        with st.spinner("Conectando..."):
            if connect_bbce():
                # Inicia thread de atualização automática
                t = Thread(target=_auto_refresh_thread, daemon=True)
                t.start()
                st.rerun()
            else:
                if st.button("Tentar novamente"):
                    st.rerun()
                return

    # --- Cabeçalho com data de atualização ---
    if st.session_state.get("ultima_atualizacao"):
        ts = st.session_state.ultima_atualizacao.strftime("%d/%m/%Y %H:%M")
        st.markdown(
            f"<p class='update-info'>Dados desde 01/01/2025 • Atualizado em {ts}</p>",
            unsafe_allow_html=True,
        )

    # --- Controles: indicadores, tipo de operação, timeframe e período ---
    col_ind, col_tipo, col_tf, col_period = st.columns([2, 1, 1, 1])
    with col_ind:
        indicadores = st.multiselect(
            "📊 Indicadores",
            options=["SMA8", "SMA20", "SMA50", "Bollinger Bands 8"],
            default=["SMA8", "SMA20"],
            key="indicadores_main",
        )
    with col_tipo:
        tipo_operacao = st.radio(
            "Tipo de operação",
            options=["Match", "Boleta"],
            index=0,
            horizontal=True,
            key="tipo_operacao",
        )
    with col_tf:
        timeframe = st.radio(
            "Timeframe",
            options=["Diário", "Semanal", "Quinzenal", "Mensal"],
            index=0,
            horizontal=True,
            key="timeframe",
        )
    with col_period:
        periodo = st.radio(
            "Período",
            options=["1M", "2M", "3M", "6M", "YTD", "ALL"],
            index=1,
            horizontal=True,
            key="periodo_main",
        )
        st.session_state.range_type = periodo

    # --- Aplica filtro de tipo de operação sobre o DataFrame bruto ---
    df_raw = st.session_state.get("df_raw", pd.DataFrame())
    if tipo_operacao == "Match":
        df_all = df_raw[df_raw["originOperationType"] == "Match"]
    else:
        df_all = df_raw  # Boleta: sem filtro por tipo

    # --- Calcula produtos disponíveis para o tipo selecionado ---
    tickers_validos = st.session_state.get("tickers", [])
    produtos = _build_produtos(df_all, tickers_validos)

    if len(produtos) < 2:
        st.warning("Não há produtos suficientes para análise.")
        return

    # --- Seleção de produtos ---
    nomes = [p["description"] for p in produtos]
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        idx1 = st.selectbox(
            "Produto A",
            options=range(len(nomes)),
            format_func=lambda x: nomes[x],
            index=0,
            key="prod1",
        )
    with col_p2:
        idx2 = st.selectbox(
            "Produto B",
            options=range(len(nomes)),
            format_func=lambda x: nomes[x],
            index=1,
            key="prod2",
        )
    with col_p3:
        st.markdown(
            "<div style='font-size:1.3rem; font-weight:500; margin-top:1.5rem;'>"
            "📊 Spread entre produtos</div>",
            unsafe_allow_html=True,
        )

    produto1 = produtos[idx1]
    produto2 = produtos[idx2]

    # --- Dados completos por produto ---
    df_raw1 = df_all[df_all["productId"] == produto1["id"]]
    df_raw2 = df_all[df_all["productId"] == produto2["id"]]

    vwap1 = calcular_vwap(df_raw1, timeframe)
    vwap2 = calcular_vwap(df_raw2, timeframe)

    df_ohlc1_full = calcular_indicadores(build_ohlc(df_raw1, timeframe), indicadores)
    df_ohlc2_full = calcular_indicadores(build_ohlc(df_raw2, timeframe), indicadores)

    # --- Filtro de período apenas para visualização ---
    range_type = st.session_state.get("range_type", "2M")
    df_ohlc1 = get_filtered_data_by_range(df_ohlc1_full, range_type)
    df_ohlc2 = get_filtered_data_by_range(df_ohlc2_full, range_type)

    # --- Gráficos ---
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.plotly_chart(
            plot_produto_com_volume(df_ohlc1, indicadores, timeframe),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with col_g2:
        st.plotly_chart(
            plot_produto_com_volume(df_ohlc2, indicadores, timeframe),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with col_g3:
        st.plotly_chart(
            plot_spread_area(df_ohlc1, df_ohlc2, produto1["description"], produto2["description"], timeframe),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # --- Tabelas OHLC ---
    col_t1, col_t2, col_t3 = st.columns(3)
    col_config = {
        "Data": st.column_config.TextColumn("Data", width="small"),
        "Open": st.column_config.NumberColumn("Abertura", format="R$ %.2f"),
        "High": st.column_config.NumberColumn("Máxima", format="R$ %.2f"),
        "Low": st.column_config.NumberColumn("Mínima", format="R$ %.2f"),
        "Close": st.column_config.NumberColumn("Fechamento", format="R$ %.2f"),
        "Pmédio": st.column_config.NumberColumn("Preço Médio", format="R$ %.2f"),
        "Vol (MWm)": st.column_config.NumberColumn("Volume", format="%d"),
    }

    with col_t1:
        tabela1 = criar_tabela_ohlc(df_ohlc1, vwap1, timeframe)
        if not tabela1.empty:
            st.dataframe(tabela1, use_container_width=True, hide_index=True,
                         height=210, column_config=col_config)
        else:
            st.info("Sem dados para exibir")

    with col_t2:
        tabela2 = criar_tabela_ohlc(df_ohlc2, vwap2, timeframe)
        if not tabela2.empty:
            st.dataframe(tabela2, use_container_width=True, hide_index=True,
                         height=210, column_config=col_config)
        else:
            st.info("Sem dados para exibir")

    with col_t3:
        st.markdown("")


if __name__ == "__main__":
    main()

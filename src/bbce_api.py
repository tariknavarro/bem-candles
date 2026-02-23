import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime

from src.secrets import get_secret as _get_secret

AMBIENTE = "https://api-ehub.bbce.com.br/"


def login_api(
    cod: int, email: str, password: str, api_key: str
) -> tuple[list | None, str | None]:
    """Realiza login na BBCE e retorna ([userId, idToken, companyId, refreshToken], erro)."""
    url = AMBIENTE + "bus/v2/login"
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json", "apiKey": api_key},
            data=json.dumps(
                {"companyExternalCode": cod, "email": email, "password": password}
            ),
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            return ([
                data["userId"],
                data["idToken"],
                data["companyId"],
                data["refreshToken"],
            ], None)
        # Erro "esperado" (credenciais, API key, etc.)
        body = (response.text or "").strip()
        body_preview = body[:500] + ("..." if len(body) > 500 else "")
        return (None, f"HTTP {response.status_code} no login. Resposta: {body_preview}")
    except requests.RequestException as e:
        return (None, f"Erro de rede no login: {e}")


def get_wallet(token: str, api_key: str) -> str | None:
    """Retorna o ID da primeira wallet encontrada."""
    url = AMBIENTE + "bus/v1/wallets"
    try:
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "apiKey": api_key,
            },
            timeout=30,
        )
        if response.status_code == 200:
            wallets = response.json()
            if wallets:
                return wallets[0]["id"]
    except requests.RequestException:
        pass
    return None


def get_negotiable_tickers(token: str, api_key: str, wallet_id: str) -> list:
    """Retorna lista de tickers negociáveis para a wallet."""
    url = AMBIENTE + f"bus/v1/negotiable-tickers?walletId={wallet_id}"
    try:
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "apiKey": api_key,
            },
            timeout=30,
        )
        if response.status_code == 200:
            return response.json().get("tickers", [])
    except requests.RequestException:
        pass
    return []


def load_deals(
    token: str, api_key: str, data_inicio: str, data_fim: str
) -> pd.DataFrame:
    """Carrega negócios do período e retorna DataFrame indexado por createdAt."""
    url = (
        AMBIENTE
        + f"bus/v1/all-deals/report?initialPeriod={data_inicio}&finalPeriod={data_fim}"
    )
    try:
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "apiKey": api_key,
            },
            timeout=60,
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                df["createdAt"] = pd.to_datetime(df["createdAt"])
                df.set_index("createdAt", inplace=True)
                return df
    except requests.RequestException as e:
        st.error(f"Erro ao carregar dados: {e}")
    return pd.DataFrame()


def connect_bbce() -> bool:
    """
    Realiza login, busca wallet e tickers, carrega deals e popula st.session_state.
    Retorna True em caso de sucesso.
    """
    api_key = _get_secret("BBCE_API_KEY")
    company_code_raw = _get_secret("BBCE_COMPANY_CODE")
    email = _get_secret("BBCE_EMAIL")
    password = _get_secret("BBCE_PASSWORD")

    missing = [
        k
        for k, v in {
            "BBCE_API_KEY": api_key,
            "BBCE_COMPANY_CODE": company_code_raw,
            "BBCE_EMAIL": email,
            "BBCE_PASSWORD": password,
        }.items()
        if not v
    ]
    if missing:
        st.error(
            "Configuração BBCE incompleta. Preencha no `.env` (veja `env.example`): "
            + ", ".join(missing)
        )
        return False

    try:
        company_code = int(company_code_raw)
    except ValueError:
        st.error("`BBCE_COMPANY_CODE` precisa ser numérico (ex.: 1447).")
        return False

    login_result, login_err = login_api(company_code, email, password, api_key)
    if not login_result:
        st.error("Falha no login com a BBCE.")
        if login_err:
            st.caption(login_err)
        return False

    token = login_result[1]
    refresh_token = login_result[3]

    wallet_id = get_wallet(token, api_key)
    if not wallet_id:
        st.error("Não foi possível encontrar a wallet.")
        return False

    tickers_raw = get_negotiable_tickers(token, api_key, wallet_id)
    tickers_validos = [
        t for t in tickers_raw if _is_valid_product_name(t.get("description", ""))
    ]

    data_inicio = "2025-01-01"
    data_fim = datetime.now().strftime("%Y-%m-%d")
    df = load_deals(token, api_key, data_inicio, data_fim)

    if df.empty:
        st.error("Nenhum dado retornado da BBCE.")
        return False

    # Guarda apenas o filtro de status; o filtro de originOperationType
    # é aplicado dinamicamente na UI conforme o seletor Match / Boleta.
    df = df[df["status"] == "Ativo"]

    st.session_state.token = token
    st.session_state.refresh_token = refresh_token
    st.session_state.api_key = api_key
    st.session_state.wallet_id = wallet_id
    st.session_state.tickers = tickers_validos
    st.session_state.df_raw = df          # DataFrame bruto (sem filtro de tipo)
    st.session_state.ultima_atualizacao = datetime.now()
    st.session_state.logado_bbce = True
    st.session_state.range_type = "2M"

    return True


def refresh_deals() -> bool:
    """Recarrega apenas os deals (para atualização periódica). Retorna True se ok."""
    if "token" not in st.session_state or not st.session_state.token:
        return False

    data_inicio = "2025-01-01"
    data_fim = datetime.now().strftime("%Y-%m-%d")
    df = load_deals(
        st.session_state.token, st.session_state.api_key, data_inicio, data_fim
    )

    if df.empty:
        return False

    df = df[df["status"] == "Ativo"]
    st.session_state.df_raw = df
    st.session_state.ultima_atualizacao = datetime.now()
    return True


def _is_valid_product_name(description: str) -> bool:
    """Retorna False para nomes no padrão 'Produto 1234' ou sem letras."""
    import re

    if not description or not isinstance(description, str):
        return False
    if re.match(r"^Produto\s+\d+$", description.strip()):
        return False
    if not any(c.isalpha() for c in description):
        return False
    return True

import os
import streamlit as st
from datetime import datetime


def check_credentials(login: str, senha: str) -> bool:
    """Valida login e senha contra variáveis de ambiente ou st.secrets."""
    expected_login = _get_secret("DASHBOARD_LOGIN")
    expected_password = _get_secret("DASHBOARD_PASSWORD")
    return login == expected_login and senha == expected_password


def _get_secret(key: str) -> str:
    """Lê segredo do st.secrets (Streamlit Cloud) ou de variável de ambiente."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")


def show_login():
    """Renderiza o formulário de login centralizado."""
    st.markdown(
        """
        <div style='display:flex; justify-content:center; align-items:center; min-height:70vh;'>
        <div style='background:white; padding:2.5rem; border-radius:10px;
                    box-shadow:0 4px 20px rgba(0,0,0,0.1); max-width:400px;
                    width:90%; border:1px solid #e9ecef;'>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h2 style='text-align:center; margin-bottom:1.5rem;'>Acesso Restrito</h2>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        login = st.text_input("Login", placeholder="Digite seu login")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Entrar", use_container_width=True)

        if submitted:
            if check_credentials(login, senha):
                st.session_state["autenticado"] = True
                st.session_state["login_time"] = datetime.now()
                st.rerun()
            else:
                st.error("Login ou senha incorretos!")

    st.markdown("</div></div>", unsafe_allow_html=True)

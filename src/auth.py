import streamlit as st
from datetime import datetime

from src.secrets import get_secret as _get_secret


def check_credentials(login: str, senha: str) -> bool:
    """Valida login e senha contra variáveis de ambiente ou st.secrets."""
    expected_login = _get_secret("DASHBOARD_LOGIN")
    expected_password = _get_secret("DASHBOARD_PASSWORD")
    if not expected_login or not expected_password:
        return False
    return login == expected_login and senha == expected_password


def show_login():
    """Renderiza a página de login centralizada e estilizada."""

    st.markdown(
        """
        <style>
        /* Esconde elementos padrão do Streamlit na tela de login */
        #MainMenu, footer, header { visibility: hidden; }

        .login-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 85vh;
        }
        .login-card {
            background: white;
            padding: 3rem 2.5rem 2rem 2.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            max-width: 420px;
            width: 100%;
            border: 1px solid #e9ecef;
        }
        .login-logo {
            text-align: center;
            margin-bottom: 0.25rem;
            font-size: 2.8rem;
        }
        .login-title {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 0.25rem;
        }
        .login-subtitle {
            text-align: center;
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 2rem;
        }
        /* Botão de submit do form */
        div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
            background-color: #1a6faf !important;
            color: white !important;
            border-radius: 8px !important;
            height: 2.8rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            width: 100% !important;
            border: none !important;
            margin-top: 0.5rem !important;
            transition: background-color 0.2s ease;
        }
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {
            background-color: #155a8a !important;
        }
        /* Inputs */
        div[data-testid="stForm"] input {
            border-radius: 8px !important;
            border: 1px solid #ced4da !important;
            padding: 0.5rem 0.75rem !important;
        }
        div[data-testid="stForm"] input:focus {
            border-color: #1a6faf !important;
            box-shadow: 0 0 0 2px rgba(26,111,175,0.15) !important;
        }
        .login-footer {
            text-align: center;
            font-size: 0.75rem;
            color: #aaa;
            margin-top: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Card centralizado via HTML
    st.markdown("<div class='login-wrapper'><div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='login-logo'>⚡</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>BEM Energia</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-subtitle'>Dashboard de Mercado — Acesso Restrito</div>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        login = st.text_input(
            "Usuário",
            placeholder="Digite seu usuário",
            label_visibility="collapsed",
        )
        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Entrar →", use_container_width=True)

        if submitted:
            if not login or not senha:
                st.warning("Preencha usuário e senha.")
            elif check_credentials(login, senha):
                st.session_state["autenticado"] = True
                st.session_state["login_time"] = datetime.now()
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    st.markdown("<div class='login-footer'>© 2026 BEM Energia · Todos os direitos reservados</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

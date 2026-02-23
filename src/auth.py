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
    """Renderiza a página de login com fundo gradiente e card moderno."""

    st.markdown(
        """
        <style>
        /* Remove padding padrão e esconde elementos do Streamlit */
        #MainMenu, footer, header { visibility: hidden; }
        .main > div { padding-top: 0 !important; }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* Fundo com gradiente animado */
        .login-bg {
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, #0f2744 0%, #1a4a7a 40%, #0d3359 70%, #071e35 100%);
            background-size: 400% 400%;
            animation: gradientShift 12s ease infinite;
            z-index: 0;
        }

        @keyframes gradientShift {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Partículas decorativas */
        .login-bg::before {
            content: '';
            position: absolute;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(26,111,175,0.15) 0%, transparent 70%);
            top: -100px;
            right: -100px;
            border-radius: 50%;
        }
        .login-bg::after {
            content: '';
            position: absolute;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(26,175,155,0.1) 0%, transparent 70%);
            bottom: -80px;
            left: -80px;
            border-radius: 50%;
        }

        /* Wrapper centralizado */
        .login-wrapper {
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 2rem;
        }

        /* Card principal */
        .login-card {
            background: rgba(255, 255, 255, 0.97);
            backdrop-filter: blur(20px);
            padding: 3rem 2.75rem 2.25rem;
            border-radius: 20px;
            box-shadow:
                0 20px 60px rgba(0, 0, 0, 0.35),
                0 4px 16px rgba(0, 0, 0, 0.15),
                inset 0 1px 0 rgba(255,255,255,0.6);
            max-width: 420px;
            width: 100%;
            border: 1px solid rgba(255,255,255,0.3);
            animation: cardIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        @keyframes cardIn {
            from { opacity: 0; transform: translateY(24px) scale(0.97); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* Logo / ícone */
        .login-logo-wrap {
            display: flex;
            justify-content: center;
            margin-bottom: 1.25rem;
        }
        .login-logo-circle {
            width: 64px;
            height: 64px;
            border-radius: 16px;
            background: linear-gradient(135deg, #1a6faf 0%, #26a69a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.9rem;
            box-shadow: 0 6px 20px rgba(26,111,175,0.4);
        }

        /* Títulos */
        .login-title {
            text-align: center;
            font-size: 1.65rem;
            font-weight: 800;
            color: #0f2744;
            margin-bottom: 0.2rem;
            letter-spacing: -0.5px;
        }
        .login-subtitle {
            text-align: center;
            font-size: 0.82rem;
            color: #8a9ab5;
            margin-bottom: 2rem;
            font-weight: 400;
        }

        /* Labels dos campos */
        .field-label {
            font-size: 0.8rem;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.35rem;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }

        /* Inputs */
        div[data-testid="stForm"] input {
            border-radius: 10px !important;
            border: 1.5px solid #e2e8f0 !important;
            padding: 0.65rem 0.9rem !important;
            font-size: 0.95rem !important;
            background: #f8fafc !important;
            color: #1a202c !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stForm"] input:focus {
            border-color: #1a6faf !important;
            background: #fff !important;
            box-shadow: 0 0 0 3px rgba(26,111,175,0.12) !important;
        }
        div[data-testid="stForm"] input::placeholder {
            color: #b0bec5 !important;
        }

        /* Botão entrar */
        div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
            background: linear-gradient(135deg, #1a6faf 0%, #1557a0 100%) !important;
            color: white !important;
            border-radius: 10px !important;
            height: 2.9rem !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            border: none !important;
            margin-top: 0.75rem !important;
            letter-spacing: 0.3px !important;
            box-shadow: 0 4px 15px rgba(26,111,175,0.4) !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {
            background: linear-gradient(135deg, #155a8a 0%, #0f4478 100%) !important;
            box-shadow: 0 6px 20px rgba(26,111,175,0.5) !important;
            transform: translateY(-1px) !important;
        }
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:active {
            transform: translateY(0) !important;
        }

        /* Divisor */
        .login-divider {
            border: none;
            border-top: 1px solid #edf2f7;
            margin: 1.75rem 0 1.25rem;
        }

        /* Footer */
        .login-footer {
            text-align: center;
            font-size: 0.72rem;
            color: #b0bec5;
        }
        .login-footer span {
            color: #90a0b7;
            font-weight: 500;
        }

        /* Alerts dentro do form */
        div[data-testid="stForm"] div[data-testid="stAlert"] {
            border-radius: 8px !important;
            font-size: 0.85rem !important;
        }
        </style>

        <div class="login-bg"></div>
        <div class="login-wrapper">
          <div class="login-card">
            <div class="login-logo-wrap">
              <div class="login-logo-circle">⚡</div>
            </div>
            <div class="login-title">BEM Energia</div>
            <div class="login-subtitle">Dashboard de Mercado &nbsp;·&nbsp; Acesso Restrito</div>
            <div class="field-label">Usuário</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        login = st.text_input(
            "Usuário",
            placeholder="Digite seu usuário",
            label_visibility="collapsed",
        )

        st.markdown("<div class='field-label' style='margin-top:0.9rem;'>Senha</div>", unsafe_allow_html=True)

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="••••••••",
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

    st.markdown(
        """
            <hr class="login-divider">
            <div class="login-footer">
              © 2026 <span>BEM Energia</span> &nbsp;·&nbsp; Todos os direitos reservados
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

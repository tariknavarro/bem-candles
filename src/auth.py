import streamlit as st
from datetime import datetime

from src.secrets import get_secret as _get_secret

# Cor principal da marca BEM Energia (verde-limão da logo)
BEM_GREEN = "#C8E600"
BEM_GREEN_DARK = "#a8c200"
BEM_NAVY = "#0f2744"


def check_credentials(login: str, senha: str) -> bool:
    """Valida login e senha contra variáveis de ambiente ou st.secrets."""
    expected_login = _get_secret("DASHBOARD_LOGIN")
    expected_password = _get_secret("DASHBOARD_PASSWORD")
    if not expected_login or not expected_password:
        return False
    return login == expected_login and senha == expected_password


def show_login():
    """Renderiza a página de login com identidade visual BEM Energia."""

    st.markdown(
        f"""
        <style>
        /* ── Reset Streamlit na tela de login ── */
        #MainMenu, footer, header {{ visibility: hidden; }}
        .main > div {{ padding-top: 0 !important; }}
        .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
        }}

        /* ── Fundo escuro fixo ── */
        .login-bg {{
            position: fixed;
            inset: 0;
            background: {BEM_NAVY};
            z-index: 0;
            overflow: hidden;
        }}

        /* Círculos decorativos com verde BEM */
        .login-bg::before {{
            content: '';
            position: absolute;
            width: 600px; height: 600px;
            border-radius: 50%;
            background: radial-gradient(circle, {BEM_GREEN}18 0%, transparent 65%);
            top: -180px; right: -180px;
        }}
        .login-bg::after {{
            content: '';
            position: absolute;
            width: 450px; height: 450px;
            border-radius: 50%;
            background: radial-gradient(circle, {BEM_GREEN}10 0%, transparent 65%);
            bottom: -120px; left: -120px;
        }}

        /* ── Faixa lateral esquerda (decoração) ── */
        .login-stripe {{
            position: fixed;
            left: 0; top: 0; bottom: 0;
            width: 6px;
            background: linear-gradient(180deg, {BEM_GREEN} 0%, {BEM_GREEN}44 100%);
            z-index: 1;
        }}

        /* ── Card ── */
        .login-card {{
            background: #ffffff;
            border-radius: 16px;
            padding: 2.5rem 2rem 2rem;
            box-shadow:
                0 24px 64px rgba(0,0,0,0.45),
                0 4px 16px rgba(0,0,0,0.2);
            border-top: 4px solid {BEM_GREEN};
            animation: cardIn 0.45s cubic-bezier(0.16,1,0.3,1) both;
            position: relative;
            z-index: 2;
        }}
        @keyframes cardIn {{
            from {{ opacity:0; transform: translateY(20px); }}
            to   {{ opacity:1; transform: translateY(0); }}
        }}

        /* ── Logo text ── */
        .bem-logo {{
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: -2px;
            color: {BEM_NAVY};
            line-height: 1;
        }}
        .bem-logo span {{
            color: {BEM_GREEN};
        }}
        .bem-tagline {{
            font-size: 0.78rem;
            color: #8a9ab5;
            font-weight: 500;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-top: 0.15rem;
            margin-bottom: 1.75rem;
        }}

        /* ── Labels ── */
        .field-label {{
            font-size: 0.72rem;
            font-weight: 700;
            color: #4a5568;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }}
        .field-gap {{ margin-top: 0.85rem; }}

        /* ── Inputs — override Streamlit ── */
        div[data-testid="stForm"] input {{
            border-radius: 8px !important;
            border: 1.5px solid #e2e8f0 !important;
            font-size: 0.9rem !important;
            background: #f9fafb !important;
            color: #1a202c !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
        }}
        div[data-testid="stForm"] input:focus {{
            border-color: {BEM_GREEN} !important;
            background: #fff !important;
            box-shadow: 0 0 0 3px {BEM_GREEN}33 !important;
            outline: none !important;
        }}
        div[data-testid="stForm"] input::placeholder {{
            color: #c0ccd8 !important;
        }}

        /* ── Botão Entrar ── */
        div[data-testid="stForm"] button[kind="primaryFormSubmit"] {{
            background: {BEM_GREEN} !important;
            color: {BEM_NAVY} !important;
            border-radius: 8px !important;
            height: 2.75rem !important;
            font-size: 0.9rem !important;
            font-weight: 800 !important;
            width: 100% !important;
            border: none !important;
            margin-top: 1rem !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 14px {BEM_GREEN}55 !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {{
            background: {BEM_GREEN_DARK} !important;
            box-shadow: 0 6px 18px {BEM_GREEN}66 !important;
            transform: translateY(-1px) !important;
        }}
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:active {{
            transform: translateY(0) !important;
        }}

        /* ── Divisor e footer ── */
        .login-sep {{
            border: none;
            border-top: 1px solid #edf2f7;
            margin: 1.5rem 0 1rem;
        }}
        .login-footer {{
            text-align: center;
            font-size: 0.7rem;
            color: #b0bec5;
        }}
        .login-footer b {{ color: #8a9ab5; font-weight: 600; }}

        /* ── Alerts ── */
        div[data-testid="stForm"] div[data-testid="stAlert"] {{
            border-radius: 8px !important;
            font-size: 0.82rem !important;
            margin-top: 0.5rem !important;
        }}
        </style>

        <div class="login-bg"></div>
        <div class="login-stripe"></div>
        """,
        unsafe_allow_html=True,
    )

    # Centraliza usando colunas do Streamlit (evita quebra de layout)
    _, col_center, _ = st.columns([1, 1.2, 1])

    with col_center:
        # Cabeçalho do card
        st.markdown(
            f"""
            <div class="login-card">
              <div class="bem-logo">bem<span>.</span></div>
              <div class="bem-tagline">energia &nbsp;·&nbsp; dashboard de mercado</div>
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

            st.markdown("<div class='field-label field-gap'>Senha</div>", unsafe_allow_html=True)

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
            <hr class="login-sep">
            <div class="login-footer">© 2026 <b>BEM Energia</b> · Todos os direitos reservados</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

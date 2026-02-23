"""
Utilitário centralizado para leitura de segredos.

Prioridade:
  1. st.secrets  (Streamlit Cloud / secrets.toml)
  2. variável de ambiente / arquivo .env

O acesso a st.secrets é feito SEM chamar __contains__ nem __getitem__
diretamente no objeto secrets — o que dispararia o aviso
'No secrets found' mesmo dentro de um try/except.
Em vez disso, inspecionamos st.secrets._secrets (dict interno) apenas
quando o arquivo já foi carregado pelo Streamlit.
"""

from __future__ import annotations

import os


def get_secret(key: str) -> str:
    """Retorna o valor do segredo ou string vazia se não encontrado."""
    # Tenta acessar os secrets do Streamlit sem disparar o aviso de console
    try:
        import streamlit as st

        # _secrets é o dict interno; é None quando nenhum arquivo foi carregado.
        internal = getattr(st.secrets, "_secrets", None)
        if isinstance(internal, dict) and key in internal:
            return str(internal[key])
    except Exception:
        pass

    # Fallback: variável de ambiente (carregada via python-dotenv no app.py)
    return os.getenv(key, "")

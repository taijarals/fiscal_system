import streamlit as st
from pathlib import Path

from pages.questoes import render as render_questoes
from pages.simulado import render as render_simulados


# ======================================================
# CONFIGURAÇÃO
# ======================================================

st.set_page_config(
    page_title="Fiscal System",
    layout="wide"
)

# ======================================================
# CSS
# ======================================================

css_path = Path(__file__).parent / "css" / "style.css"

if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )

# ======================================================
# AUTENTICAÇÃO
# ======================================================


def obter_credenciais():
    try:
        secao_auth = st.secrets.get("auth", {})
        usuario = st.secrets.get("AUTH_USERNAME") or secao_auth.get("username")
        senha = st.secrets.get("AUTH_PASSWORD") or secao_auth.get("password")
    except Exception:
        return None, None

    return usuario, senha


def autenticar(usuario, senha):
    usuario_config, senha_config = obter_credenciais()

    if usuario_config and senha_config:
        return usuario == usuario_config and senha == senha_config

    return usuario == "admin" and senha == "admin123"


def render_login():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("### Acesso ao sistema")
    st.caption("Informe suas credenciais para continuar.")

    with st.form("login_form"):
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        enviado = st.form_submit_button("Entrar", use_container_width=True, type="primary")

        if enviado:
            if autenticar(usuario, senha):
                st.session_state.authenticated = True
                st.session_state.username = usuario
                st.session_state.page = "Questões"
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption(
        "Credenciais padrão: admin / admin123. Para produção, configure AUTH_USERNAME e AUTH_PASSWORD em .streamlit/secrets.toml."
    )


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Questões"

# ======================================================
# HEADER
# ======================================================

st.markdown("## Fiscal System")

if st.session_state.authenticated:
    st.caption(f"Usuário autenticado: {st.session_state.username}")

# ======================================================
# MENU
# ======================================================

if st.session_state.authenticated:
    col1, col2, col3, col4 = st.columns([2.5, 2.5, 2.5, 1.5])

    with col1:
        if st.button(
            "Questões",
            width='stretch',
            type="primary" if st.session_state.page == "Questões" else "secondary"
        ):
            st.session_state.page = "Questões"

    with col2:
        if st.button(
            "Simulados",
            width='stretch',
            type="primary" if st.session_state.page == "Simulados" else "secondary"
        ):
            st.session_state.page = "Simulados"

    with col3:
        if st.button(
            "Indicadores",
            width='stretch',
            type="primary" if st.session_state.page == "Indicadores" else "secondary"
        ):
            st.session_state.page = "Indicadores"

    with col4:
        if st.button("Sair", width='stretch', type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.page = "Questões"
            st.rerun()

    st.divider()

    # ======================================================
    # CONTEÚDO
    # ======================================================

    if st.session_state.page == "Questões":
        render_questoes()

    elif st.session_state.page == "Simulados":
        render_simulados()

    elif st.session_state.page == "Indicadores":
        st.subheader("Indicadores")
else:
    render_login()
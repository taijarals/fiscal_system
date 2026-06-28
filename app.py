from pathlib import Path

import requests
import streamlit as st

from pages.indicadores import render as render_indicadores
from pages.questoes import obter_config_supabase, render as render_questoes
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


def autenticar(usuario, senha):
    url, key = obter_config_supabase()

    if url and key:
        try:
            resposta = requests.post(
                f"{url}/auth/v1/token?grant_type=password",
                headers={
                    "apikey": key,
                    "Content-Type": "application/json",
                },
                json={"email": usuario, "password": senha},
                timeout=15,
            )
            resposta.raise_for_status()
            dados = resposta.json()
            st.session_state.auth_token = dados.get("access_token")
            st.session_state.auth_user = dados.get("user", {})
            return True
        except Exception:
            st.session_state.auth_token = None
            st.session_state.auth_user = {}
            return False

    return usuario == "admin" and senha == "admin123"


def criar_usuario_supabase(email, senha):
    url, key = obter_config_supabase()

    if not (url and key):
        return False, "Cadastro via Supabase não está configurado."

    try:
        resposta = requests.post(
            f"{url}/auth/v1/signup",
            headers={
                "apikey": key,
                "Content-Type": "application/json",
            },
            json={"email": email, "password": senha},
            timeout=15,
        )
        resposta.raise_for_status()
        return True, "Usuário criado com sucesso. Você já pode entrar."
    except Exception as erro:
        mensagem = str(erro)
        if "User already registered" in mensagem:
            return False, "Este e-mail já está cadastrado."
        return False, f"Não foi possível criar o usuário: {mensagem}"


def render_login():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("### Acesso ao sistema")
    st.caption("Entre com sua conta do Supabase Auth ou use o acesso local de desenvolvimento.")

    tab_login, tab_cadastro = st.tabs(["Entrar", "Criar conta"])

    with tab_login:
        with st.form("login_form"):
            usuario = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            enviado = st.form_submit_button("Entrar", use_container_width=True, type="primary")

            if enviado:
                if autenticar(usuario, senha):
                    st.session_state.authenticated = True
                    st.session_state.username = usuario
                    st.session_state.page = "Questões"
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")

    with tab_cadastro:
        with st.form("signup_form"):
            novo_email = st.text_input("E-mail", placeholder="novo@email.com", key="signup_email")
            nova_senha = st.text_input("Senha", type="password", placeholder="Crie uma senha", key="signup_senha")
            confirmar_senha = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha", key="signup_confirmar")
            cadastrar = st.form_submit_button("Criar conta", use_container_width=True, type="primary")

            if cadastrar:
                if not novo_email or not nova_senha:
                    st.error("Preencha e-mail e senha para criar a conta.")
                elif nova_senha != confirmar_senha:
                    st.error("As senhas não coincidem.")
                else:
                    sucesso, mensagem = criar_usuario_supabase(novo_email, nova_senha)
                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption(
        "Se estiver usando o Supabase, crie o usuário no painel de Auth ou pela aba acima. Sem configuração, o fallback é admin/admin123."
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
        render_indicadores()
else:
    render_login()
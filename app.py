import streamlit as st
from pathlib import Path

from pages.questoes import render as render_questoes


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
# SESSION STATE
# ======================================================

if "page" not in st.session_state:
    st.session_state.page = "Questões"

# ======================================================
# HEADER
# ======================================================

st.markdown("## Fiscal System")

# ======================================================
# MENU
# ======================================================

col1, col2, col3 = st.columns(3)

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

st.divider()

# ======================================================
# CONTEÚDO
# ======================================================

if st.session_state.page == "Questões":

    render_questoes()

elif st.session_state.page == "Simulados":

    st.subheader("Simulados")

elif st.session_state.page == "Indicadores":

    st.subheader("Indicadores")
import streamlit as st
from pathlib import Path
from pages.questoes import render as render_questoes

st.set_page_config(
    page_title="Fiscal System",
    layout="wide"
)

css_path = Path(__file__).parent / "css" / "style.css"

if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )

if "page" not in st.session_state:
    st.session_state.page = "Questões"

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        "Questões",
        use_container_width=True,
        type="primary" if st.session_state.page == "Questões" else "secondary"
    ):
        st.session_state.page = "Questões"

with col2:
    if st.button(
        "Simulados",
        use_container_width=True,
        type="primary" if st.session_state.page == "Simulados" else "secondary"
    ):
        st.session_state.page = "Simulados"

with col3:
    if st.button(
        "Indicadores",
        use_container_width=True,
        type="primary" if st.session_state.page == "Indicadores" else "secondary"
    ):
        st.session_state.page = "Indicadores"

st.divider()

st.title("Fiscal System")

with st.container(border=True):

    if st.session_state.page == "Questões":
        render_questoes()

    elif st.session_state.page == "Simulados":
        st.subheader("Simulados")
        st.write(
            "Acesse simulados organizados por tema e nível de dificuldade."
        )

    elif st.session_state.page == "Indicadores":
        st.subheader("Indicadores")
        st.write(
            "Veja os indicadores de desempenho e progresso do seu estudo."
        )
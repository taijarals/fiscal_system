import streamlit as st
import pandas as pd


def render():

    if "questoes" not in st.session_state:
        st.session_state.questoes = [
            {
                "id": 1,
                "disciplina": "ICMS",
                "assunto": "Crédito Fiscal",
                "titulo": "Questão ICMS 001",
                "enunciado": "Qual a alíquota interna da Bahia?",
                "correta": "B"
            },
            {
                "id": 2,
                "disciplina": "IPI",
                "assunto": "Industrialização",
                "titulo": "Questão IPI 001",
                "enunciado": "O que caracteriza industrialização?",
                "correta": "A"
            }
        ]

    # ==================================================
    # TOOLBAR
    # ==================================================

    col1, col2 = st.columns([8, 2])

    with col1:
        st.subheader("Questões")

    with col2:
        nova_questao = st.button(
            "Nova Questão",
            use_container_width=True
        )

    st.divider()

    # ==================================================
    # FILTROS
    # ==================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        disciplina = st.selectbox(
            "Disciplina",
            ["Todas"]
        )

    with col2:
        assunto = st.selectbox(
            "Assunto",
            ["Todos"]
        )

    with col3:
        pesquisa = st.text_input(
            "Pesquisar"
        )

    st.divider()

    # ==================================================
    # TABELA
    # ==================================================

    df = pd.DataFrame(st.session_state.questoes)

    colunas = [
        "id",
        "disciplina",
        "assunto",
        "titulo",
        "correta"
    ]

    st.dataframe(
        df[colunas],
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # FORMULÁRIO
    # ==================================================

    if nova_questao:

        @st.dialog("Nova Questão")
        def formulario():

            with st.form("nova_questao"):

                disciplina = st.text_input("Disciplina")

                assunto = st.text_input("Assunto")

                titulo = st.text_input("Título")

                enunciado = st.text_area("Enunciado")

                correta = st.selectbox(
                    "Resposta Correta",
                    ["A", "B", "C", "D"]
                )

                salvar = st.form_submit_button(
                    "Salvar",
                    use_container_width=True
                )

                if salvar:

                    novo_id = (
                        max(
                            [q["id"] for q in st.session_state.questoes],
                            default=0
                        ) + 1
                    )

                    st.session_state.questoes.append(
                        {
                            "id": novo_id,
                            "disciplina": disciplina,
                            "assunto": assunto,
                            "titulo": titulo,
                            "enunciado": enunciado,
                            "correta": correta
                        }
                    )

                    st.rerun()

        formulario()
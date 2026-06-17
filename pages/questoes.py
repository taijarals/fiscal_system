import streamlit as st
import pandas as pd


def render():

    st.title("📚 Questões")

    # =====================================================
    # DADOS MOCKADOS
    # =====================================================

    if "questoes" not in st.session_state:
        st.session_state.questoes = [
            {
                "id": 1,
                "disciplina": "ICMS",
                "assunto": "Crédito Fiscal",
                "titulo": "Questão ICMS 001",
                "enunciado": "Qual a alíquota interna da Bahia?",
                "correta": "B",
            },
            {
                "id": 2,
                "disciplina": "IPI",
                "assunto": "Industrialização",
                "titulo": "Questão IPI 001",
                "enunciado": "O que caracteriza industrialização?",
                "correta": "A",
            },
        ]

    if "modo_edicao" not in st.session_state:
        st.session_state.modo_edicao = False

    if "questao_edicao" not in st.session_state:
        st.session_state.questao_edicao = None

    # =====================================================
    # CABEÇALHO
    # =====================================================

    col1, col2 = st.columns([8, 1])

    with col1:
        st.subheader("Cadastro de Questões")

    with col2:
        if st.button("➕ Nova"):
            st.session_state.modo_edicao = False
            st.session_state.questao_edicao = None

    st.divider()

    # =====================================================
    # FILTROS
    # =====================================================

    st.markdown("### Filtros")

    col1, col2, col3 = st.columns(3)

    disciplinas = sorted(
        list(
            set(
                q["disciplina"]
                for q in st.session_state.questoes
            )
        )
    )

    assuntos = sorted(
        list(
            set(
                q["assunto"]
                for q in st.session_state.questoes
            )
        )
    )

    with col1:
        filtro_disciplina = st.selectbox(
            "Disciplina",
            ["Todas"] + disciplinas
        )

    with col2:
        filtro_assunto = st.selectbox(
            "Assunto",
            ["Todos"] + assuntos
        )

    with col3:
        filtro_texto = st.text_input(
            "Pesquisar"
        )

    # =====================================================
    # FILTRAGEM
    # =====================================================

    questoes_filtradas = st.session_state.questoes.copy()

    if filtro_disciplina != "Todas":
        questoes_filtradas = [
            q for q in questoes_filtradas
            if q["disciplina"] == filtro_disciplina
        ]

    if filtro_assunto != "Todos":
        questoes_filtradas = [
            q for q in questoes_filtradas
            if q["assunto"] == filtro_assunto
        ]

    if filtro_texto:
        questoes_filtradas = [
            q for q in questoes_filtradas
            if filtro_texto.lower()
            in q["titulo"].lower()
        ]

    st.divider()

    # =====================================================
    # LISTAGEM
    # =====================================================

    st.markdown("### Questões")

    for questao in questoes_filtradas:

        col1, col2, col3, col4, col5 = st.columns(
            [1, 4, 2, 1, 1]
        )

        with col1:
            st.write(questao["id"])

        with col2:
            st.write(questao["titulo"])

        with col3:
            st.write(questao["disciplina"])

        with col4:

            if st.button(
                "✏️",
                key=f"editar_{questao['id']}"
            ):
                st.session_state.modo_edicao = True
                st.session_state.questao_edicao = questao

                st.rerun()

        with col5:

            if st.button(
                "🗑️",
                key=f"excluir_{questao['id']}"
            ):

                st.session_state.questoes = [
                    q
                    for q in st.session_state.questoes
                    if q["id"] != questao["id"]
                ]

                st.rerun()

    st.divider()

    # =====================================================
    # FORMULÁRIO
    # =====================================================

    titulo_form = (
        "Editar Questão"
        if st.session_state.modo_edicao
        else "Nova Questão"
    )

    st.markdown(f"## {titulo_form}")

    questao = st.session_state.questao_edicao

    with st.form("form_questao"):

        disciplina = st.text_input(
            "Disciplina",
            value=questao["disciplina"]
            if questao
            else ""
        )

        assunto = st.text_input(
            "Assunto",
            value=questao["assunto"]
            if questao
            else ""
        )

        titulo = st.text_input(
            "Título",
            value=questao["titulo"]
            if questao
            else ""
        )

        enunciado = st.text_area(
            "Enunciado",
            value=questao["enunciado"]
            if questao
            else ""
        )

        correta = st.selectbox(
            "Resposta Correta",
            ["A", "B", "C", "D"],
            index=["A", "B", "C", "D"].index(
                questao["correta"]
            )
            if questao
            else 0
        )

        salvar = st.form_submit_button(
            "Salvar",
            use_container_width=True
        )

    # =====================================================
    # SALVAR
    # =====================================================

    if salvar:

        if st.session_state.modo_edicao:

            questao["disciplina"] = disciplina
            questao["assunto"] = assunto
            questao["titulo"] = titulo
            questao["enunciado"] = enunciado
            questao["correta"] = correta

            st.success("Questão atualizada.")

        else:

            novo_id = max(
                [q["id"] for q in st.session_state.questoes],
                default=0
            ) + 1

            st.session_state.questoes.append(
                {
                    "id": novo_id,
                    "disciplina": disciplina,
                    "assunto": assunto,
                    "titulo": titulo,
                    "enunciado": enunciado,
                    "correta": correta,
                }
            )

            st.success("Questão cadastrada.")

        st.rerun()
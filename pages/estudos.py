import streamlit as st
import streamlit.components.v1 as components


def criar_estrutura_exemplo():
    return {
        "Ciclos 1": {
            "Meta 1": {
                "ICMS / Crédito Fiscal": {
                    "Aulas": ["Aula 1: Introdução", "Aula 2: Conceitos", "Aula 3: Exemplos"],
                    "PDF": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                }
            }
        }
    }


def render_arvore(esquerda, estrutura):
    for ciclo, metas in estrutura.items():
        with esquerda.expander(ciclo, expanded=True):
            for meta, disciplinas in metas.items():
                with esquerda.expander(meta, expanded=True):
                    for disciplina, conteudo in disciplinas.items():
                        with esquerda.expander(disciplina, expanded=False):
                            aulas = conteudo.get("Aulas", [])
                            for i, aula in enumerate(aulas, start=1):
                                key = f"{ciclo}-{meta}-{disciplina}-aula-{i}"
                                if esquerda.button(aula, key=key):
                                    st.session_state.estudo_selecionado = {
                                        "tipo": "aula",
                                        "titulo": aula,
                                        "disciplina": disciplina,
                                        "ciclo": ciclo,
                                        "meta": meta,
                                    }
                                    st.experimental_rerun()

                            pdf = conteudo.get("PDF")
                            if pdf:
                                key_pdf = f"{ciclo}-{meta}-{disciplina}-pdf"
                                if esquerda.button("Abrir PDF", key=key_pdf):
                                    st.session_state.estudo_selecionado = {
                                        "tipo": "pdf",
                                        "url": pdf,
                                        "disciplina": disciplina,
                                        "ciclo": ciclo,
                                        "meta": meta,
                                    }
                                    st.experimental_rerun()

    return st.session_state.get("estudo_selecionado")


def mostrar_pdf_url(url):
    try:
        components.iframe(url, height=700)
    except Exception:
        st.error("Não foi possível incorporar o PDF. Verifique a URL.")


def render():
    st.set_page_config(layout="wide")

    st.title("Área de Estudos")

    estrutura = criar_estrutura_exemplo()

    esquerda, direita = st.columns([1, 3])

    with esquerda:
        st.header("Conteúdo")
        st.caption("Selecione Ciclo → Meta → Disciplina → Aula/PDF")
        render_arvore(esquerda, estrutura)

        st.divider()
        st.write("\n")

    with direita:
        selecionado = st.session_state.get("estudo_selecionado")

        if selecionado:
            if selecionado["tipo"] == "aula":
                st.subheader(selecionado["titulo"])
                st.markdown("Conteúdo da aula — insira material, vídeo ou notas aqui.")
            elif selecionado["tipo"] == "pdf":
                st.subheader(f"PDF — {selecionado.get('disciplina')}")
                mostrar_pdf_url(selecionado["url"])
        else:
            st.subheader("Bem-vindo à área de estudos")
            st.write("Escolha uma aula ou PDF à esquerda para começar.")


if __name__ == "__main__":
    render()

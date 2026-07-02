import streamlit as st
import streamlit.components.v1 as components


def criar_estrutura_exemplo():
    return {
        "Ciclo 1": {
            "Meta 1": {
                "Direito Tributário": {
                    "Aulas": [
                        {
                            "titulo": "Aula 1: Introdução ao Direito Tributário 01 a 08",
                            "url": "https://videoaulas.infra.grancursosonline.com.br/564afe295161b94c3dcc76ab8ec071b3/d414bb4a431beb9bf948835085c9340b/d414bb4a431beb9bf948835085c9340b-p480.mp4?Expires=1783109998&Signature=TmjkInm6iFIHqHbfIBIM5IlVPWyGlLuDr4dOzDr3rIIXoEDqRUbzKrAmLResO-QajDSdohqYe4TJ9pAukUcBxd~WXS7s1Stbc5-nZPPMcsDqySkI5DqK3~i3w3OT~UWYjNZEMrDxNYR0HqFwloak22cAxWDjX8kJI9RQpHZAwWxSG8kqfDxaUXQxcVDCM66qlWfFhDYzVC~qvzupQDgbLcPy7YmDq93tLxxtey-4Am-PMcym9WlaSFF5EhAdSV6TKvrFiVZDkBzk8V2SjZTb-Q4-1en4hl9lAzkZYQ4n5o6tz-0g-DBHle5ubJwaW9RZNjisdU1ONkvQxRyHl6dAcQ__&Key-Pair-Id=APKAJWDRH5QWMLF2KNSA"
                        }
                    ],
                    "PDF": None,
                    "Questoes": [],
                    "Tipo": "Vídeo",
                }
            }
        }
    }


def render_arvore(esquerda, estrutura):
    for ciclo, metas in estrutura.items():
        with esquerda.expander(ciclo, expanded=False):
            for meta, disciplinas in metas.items():
                with esquerda.expander(meta, expanded=False):
                    for disciplina, conteudo in disciplinas.items():
                        with esquerda.expander(disciplina, expanded=False):
                            aulas = conteudo.get("Aulas", [])
                            for i, aula in enumerate(aulas, start=1):
                                title = aula["titulo"] if isinstance(aula, dict) else str(aula)
                                key = f"{ciclo}-{meta}-{disciplina}-aula-{i}"
                                if esquerda.button(title, key=key):
                                    if isinstance(aula, dict) and aula.get("url"):
                                        st.session_state.estudo_selecionado = {
                                            "tipo": "video",
                                            "titulo": title,
                                            "url": aula.get("url"),
                                            "disciplina": disciplina,
                                            "ciclo": ciclo,
                                            "meta": meta,
                                        }
                                    else:
                                        st.session_state.estudo_selecionado = {
                                            "tipo": "aula",
                                            "titulo": title,
                                            "disciplina": disciplina,
                                            "ciclo": ciclo,
                                            "meta": meta,
                                        }
                                    st.rerun()

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
                                    st.rerun()

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
            elif selecionado["tipo"] == "video":
                st.subheader(selecionado["titulo"])
                try:
                    st.video(selecionado["url"], start_time=0)
                except Exception:
                    st.error("Não foi possível reproduzir o vídeo. Verifique a URL.")
            elif selecionado["tipo"] == "pdf":
                st.subheader(f"PDF — {selecionado.get('disciplina')}")
                mostrar_pdf_url(selecionado["url"])
        else:
            st.subheader("Bem-vindo à área de estudos")
            st.write("Escolha uma aula ou PDF à esquerda para começar.")


if __name__ == "__main__":
    render()

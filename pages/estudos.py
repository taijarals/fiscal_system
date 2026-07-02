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
    # Inicializa estado de expansões
    if "tree_expanded" not in st.session_state:
        st.session_state["tree_expanded"] = {}

    def is_expanded(path):
        return st.session_state["tree_expanded"].get(path, False)

    def toggle_expanded(path):
        st.session_state["tree_expanded"][path] = not st.session_state["tree_expanded"].get(path, False)

    def render_node(name, data, path, level):
        indent = "\u00A0" * (level * 4)

        # Internal node (dict with children)
        if isinstance(data, dict) and any(k not in ("Aulas", "PDF", "Questoes", "Tipo") for k in data.keys()):
            key_btn = f"node-{path}"
            caret = "▾" if is_expanded(path) else "▸"
            label = f"{indent}{caret} {name}"
            if esquerda.button(label, key=key_btn):
                toggle_expanded(path)
                st.rerun()

            if is_expanded(path):
                # render children
                for child_name, child_data in data.items():
                    render_node(child_name, child_data, f"{path}/{child_name}", level + 1)

        else:
            # Node that may contain Aulas/PDF directly
            key_btn = f"node-{path}"
            caret = "▾" if is_expanded(path) else "▸" if isinstance(data, dict) else ""
            label = f"{indent}{caret} {name}"
            if esquerda.button(label, key=key_btn):
                # if has aulas
                aulas = data.get("Aulas") if isinstance(data, dict) else None
                if aulas:
                    toggle_expanded(path)
                    st.rerun()
                else:
                    # leaf without aulas (unlikely) — select
                    st.session_state.estudo_selecionado = {"tipo": "node", "titulo": name}
                    st.rerun()

            if isinstance(data, dict) and is_expanded(path):
                # render Aulas
                aulas = data.get("Aulas", [])
                for i, aula in enumerate(aulas, start=1):
                    title = aula.get("titulo") if isinstance(aula, dict) else str(aula)
                    key_a = f"{path}-aula-{i}"
                    label_a = f"{indent}\u00A0\u00A0▶ {title}"
                    if esquerda.button(label_a, key=key_a):
                        if isinstance(aula, dict) and aula.get("url"):
                            st.session_state.estudo_selecionado = {
                                "tipo": "video",
                                "titulo": title,
                                "url": aula.get("url"),
                                "path": path,
                            }
                        else:
                            st.session_state.estudo_selecionado = {"tipo": "aula", "titulo": title, "path": path}
                        st.rerun()

                pdf = data.get("PDF")
                if pdf:
                    key_pdf = f"{path}-pdf"
                    label_pdf = f"{indent}\u00A0\u00A0📄 PDF"
                    if esquerda.button(label_pdf, key=key_pdf):
                        st.session_state.estudo_selecionado = {"tipo": "pdf", "url": pdf, "path": path}
                        st.rerun()

    # Render top-level nodes
    for top_name, top_data in estrutura.items():
        render_node(top_name, top_data, top_name, 0)

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

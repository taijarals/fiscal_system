import streamlit as st
import streamlit.components.v1 as components
from functools import partial

# tentativas de import do componente 'streamlit-tree-select'
try:
    from streamlit_tree_select import tree_select as st_tree_select
except Exception:
    st_tree_select = None


def criar_estrutura_exemplo():
    return {
        "Ciclo 1": {
            "Meta 1": {
                "Direito Tributário": {
                    "Introdução ao Direito Tributário": {
                        "Aulas": [
                            {"titulo": "Aula 1", "url": "https://videoaulas.infra.grancursosonline.com.br/564afe295161b94c3dcc76ab8ec071b3/d414bb4a431beb9bf948835085c9340b/d414bb4a431beb9bf948835085c9340b-p480.mp4?Expires=1783109998&Signature=TmjkInm6iFIHqHbfIBIM5IlVPWyGlLuDr4dOzDr3rIIXoEDqRUbzKrAmLResO-QajDSdohqYe4TJ9pAukUcBxd~WXS7s1Stbc5-nZPPMcsDqySkI5DqK3~i3w3OT~UWYjNZEMrDxNYR0HqFwloak22cAxWDjX8kJI9RQpHZAwWxSG8kqfDxaUXQxcVDCM66qlWfFhDYzVC~qvzupQDgbLcPy7YmDq93tLxxtey-4Am-PMcym9WlaSFF5EhAdSV6TKvrFiVZDkBzk8V2SjZTb-Q4-1en4hl9lAzkZYQ4n5o6tz-0g-DBHle5ubJwaW9RZNjisdU1ONkvQxRyHl6dAcQ__&Key-Pair-Id=APKAJWDRH5QWMLF2KNSA"},
                            {"titulo": "Aula 2"},
                            {"titulo": "Aula 3"},
                            {"titulo": "Aula 4"},
                            {"titulo": "Aula 5"},
                            {"titulo": "Aula 6"},
                            {"titulo": "Aula 7"},
                            {"titulo": "Aula 8"},
                        ],
                        "PDF": None,
                        "Questoes": [],
                        "Tipo": "Vídeo",
                    }
                }
            }
        }
    }


def render_arvore(esquerda, estrutura):
    for ciclo_nome, ciclo_dados in estrutura.items():
        with esquerda.expander(ciclo_nome, expanded=False):
            for meta_nome, meta_dados in ciclo_dados.items():
                with esquerda.expander(meta_nome, expanded=False):
                    for disciplina_nome, disciplina_dados in meta_dados.items():
                        with esquerda.expander(disciplina_nome, expanded=False):
                            for topico_nome, topico_dados in disciplina_dados.items():
                                with esquerda.expander(topico_nome, expanded=False):
                                    aulas = topico_dados.get("Aulas", [])
                                    for i, aula in enumerate(aulas, start=1):
                                        title = aula.get("titulo") if isinstance(aula, dict) else str(aula)
                                        key = f"{ciclo_nome}-{meta_nome}-{disciplina_nome}-{topico_nome}-aula-{i}"
                                        if esquerda.button(title, key=key):
                                            if isinstance(aula, dict) and aula.get("url"):
                                                st.session_state.estudo_selecionado = {
                                                    "tipo": "video",
                                                    "titulo": title,
                                                    "url": aula.get("url"),
                                                    "path": f"{ciclo_nome}/{meta_nome}/{disciplina_nome}/{topico_nome}",
                                                }
                                            else:
                                                st.session_state.estudo_selecionado = {
                                                    "tipo": "aula",
                                                    "titulo": title,
                                                    "path": f"{ciclo_nome}/{meta_nome}/{disciplina_nome}/{topico_nome}",
                                                }
                                            st.experimental_rerun()

                                    pdf = topico_dados.get("PDF")
                                    if pdf:
                                        key_pdf = f"{ciclo_nome}-{meta_nome}-{disciplina_nome}-{topico_nome}-pdf"
                                        if esquerda.button("Abrir PDF", key=key_pdf):
                                            st.session_state.estudo_selecionado = {
                                                "tipo": "pdf",
                                                "url": pdf,
                                                "path": f"{ciclo_nome}/{meta_nome}/{disciplina_nome}/{topico_nome}",
                                            }
                                            st.experimental_rerun()

    return st.session_state.get("estudo_selecionado")


def mostrar_pdf_url(url):
    try:
        components.iframe(url, height=700)
    except Exception:
        st.error("Não foi possível incorporar o PDF. Verifique a URL.")


def render():
    st.title("Área de Estudos")

    estrutura = criar_estrutura_exemplo()

    esquerda, direita = st.columns([1, 3])

    with esquerda:
        st.header("Conteúdo")
        st.caption("Selecione Ciclo → Meta → Disciplina → Aula/PDF")
        # Preferir usar streamlit-tree-select quando disponível
        selecionado = None
        if st_tree_select:
            # Construir nodes no formato esperado pelo componente
            def construir_nodos(obj, path=""):
                nodos = []
                for nome, valor in obj.items():
                    novo_path = f"{path}/{nome}".lstrip("/")
                    nodo = {"label": nome, "value": novo_path}
                    # Se o valor for dict e contém chaves de conteúdo
                    if isinstance(valor, dict):
                        # Se tem 'Aulas', transformar cada aula em child
                        if "Aulas" in valor:
                            children = []
                            for i, aula in enumerate(valor.get("Aulas", []), start=1):
                                titulo = aula.get("titulo") if isinstance(aula, dict) else str(aula)
                                aula_path = f"{novo_path}/Aula {i}"
                                child = {"label": titulo, "value": aula_path}
                                # guardar URL no map para reprodução
                                if isinstance(aula, dict) and aula.get("url"):
                                    child["meta"] = {"url": aula.get("url"), "tipo": "video"}
                                children.append(child)

                            # PDF
                            if valor.get("PDF"):
                                pdf_path = f"{novo_path}/PDF"
                                children.append({"label": "PDF", "value": pdf_path, "meta": {"url": valor.get("PDF"), "tipo": "pdf"}})

                            nodo["children"] = children
                        else:
                            nodo["children"] = construir_nodos(valor, novo_path)
                    nodos.append(nodo)
                return nodos

            tree_data = construir_nodos(estrutura)

            # Mostrar componente e obter seleção
            try:
                selecionados = st_tree_select(tree_data, key="tree_select")
            except Exception:
                st.warning("Erro ao renderizar streamlit-tree-select; usando fallback.")
                selecionados = None

            # Mapear seleção para ação
            if selecionados:
                # selecionados geralmente é lista; pegar o último selecionado
                sel = selecionados[-1] if isinstance(selecionados, (list, tuple)) else selecionados
                # procurar meta nos nodes para achar url
                def procurar_meta(nodes, value):
                    for n in nodes:
                        if n.get("value") == value:
                            return n.get("meta")
                        if "children" in n:
                            res = procurar_meta(n["children"], value)
                            if res:
                                return res
                    return None

                meta = procurar_meta(tree_data, sel)
                if meta:
                    if meta.get("tipo") == "video":
                        st.session_state.estudo_selecionado = {"tipo": "video", "titulo": sel.split("/")[-1], "url": meta.get("url")}
                    elif meta.get("tipo") == "pdf":
                        st.session_state.estudo_selecionado = {"tipo": "pdf", "url": meta.get("url")}
        else:
            selecionado = render_arvore(esquerda, estrutura)

        # se usamos tree-select, render_arvore não foi chamada e estado pode ter sido setado
        if not st_tree_select:
            selecionado = selecionado
        else:
            selecionado = st.session_state.get("estudo_selecionado")

        st.divider()
        st.write("\n")

    with direita:
        selecionado = st.session_state.get("estudo_selecionado")

        if selecionado:
            if selecionado["tipo"] == "aula":
                st.subheader(selecionado["titulo"])
                st.markdown("Conteúdo da aula — insira material, vídeo ou notas aqui.")
            elif selecionado["tipo"] == "video":
                # Mostrar título fixo com link da aula, conforme solicitado
                st.markdown("## Fenômeno da Incidência Tributária e Fato Gerador")
                st.markdown(f"[Abrir link da aula]({selecionado['url']})")
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

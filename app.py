from typing import Dict

import streamlit as st

from backend import (
    ATTACHMENTS_ROOT,
    ResourceItem,
    build_summary,
    collect_resources,
    create_pdf_embed,
    get_filtered_resources,
    load_tracking_state,
    save_tracking_state,
    scan_folder,
)
from frontend import (
    load_css,
    render_header,
    render_popup,
    render_sidebar,
    render_status_bar,
    render_timeline_card,
    render_tree_panel,
)


def get_popup_html(resource: ResourceItem) -> str:
    if resource.type == "video" and resource.url:
        return (
            f"<video controls style='width:100%; max-height:720px; border-radius: 18px;'>"
            f"<source src='{resource.url}' type='video/mp4'>"
            "Seu navegador não suporta vídeo HTML5."
            "</video>"
        )
    if resource.type == "pdf":
        return create_pdf_embed(resource.file_path)

    if resource.type == "file":
        try:
            content = resource.file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            content = "Não foi possível carregar o arquivo."
        content = content.replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre style='white-space: pre-wrap; word-wrap: break-word; color: #e2e8f0;'>{content}</pre>"

    if resource.url:
        return f"<a href='{resource.url}' target='_blank' class='card-button'>Abrir recurso</a>"

    return "<div class='alert error'>Nenhuma visualização disponível para este recurso.</div>"


def get_open_item_id() -> str | None:
    return st.session_state.get("open_item")


def set_open_item_id(item_id: str) -> None:
    st.session_state["open_item"] = item_id


def clear_open_item_id() -> None:
    st.session_state["open_item"] = None


def main() -> None:
    st.set_page_config(page_title="Acompanhamento de Metas", layout="wide")
    load_css()
    render_header()

    if not ATTACHMENTS_ROOT.exists():
        st.error("A pasta `attachments/` não foi encontrada. Crie a pasta ou ajuste o caminho no arquivo `app.py`.")
        return

    tracking_state: Dict[str, bool] = load_tracking_state()
    tree = scan_folder(ATTACHMENTS_ROOT)
    resources = collect_resources(tree)

    for item in resources:
        item.completed = tracking_state.get(item.id, False)

    summary = build_summary(resources)
    weeks = ["Todas"] + sorted({item.week for item in resources if item.week})
    metas = ["Todas"] + sorted({item.meta for item in resources if item.meta})
    disciplines = ["Todas"] + sorted({item.discipline for item in resources if item.discipline})
    selected_week, selected_meta, selected_discipline = render_sidebar(summary, weeks, metas, disciplines)

    filtered_resources = get_filtered_resources(resources, selected_week, selected_meta, selected_discipline)
    if not filtered_resources:
        st.info("Nenhum recurso encontrado com os filtros atuais.")
        return

    if "open_item" not in st.session_state:
        st.session_state["open_item"] = None

    open_item_id = get_open_item_id()
    open_item = next((item for item in filtered_resources if item.id == open_item_id), None)

    completed_count = sum(item.completed for item in filtered_resources)
    render_status_bar(completed_count, len(filtered_resources))

    col_tree, col_timeline = st.columns([1, 2])
    with col_tree:
        render_tree_panel(filtered_resources)
    with col_timeline:
        st.subheader("Timeline de conteúdos")
        for item in filtered_resources:
            render_timeline_card(item, item.id == open_item_id)
            cols = st.columns([1, 2, 2])
            with cols[0]:
                if st.button("Abrir", key=f"open_button_{item.id}"):
                    set_open_item_id(item.id)
            with cols[1]:
                checkbox_val = st.checkbox("Concluído", value=item.completed, key=f"done_{item.id}")
                if checkbox_val != item.completed:
                    tracking_state[item.id] = checkbox_val
                    item.completed = checkbox_val
            with cols[2]:
                st.write(" ")

    if open_item:
        st.button("×", key="close_popup", help="Fechar popup", on_click=clear_open_item_id)
        popup_html = get_popup_html(open_item)
        render_popup(open_item, popup_html)

    save_tracking_state({item.id: item.completed for item in resources})


if __name__ == "__main__":
    main()

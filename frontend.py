from pathlib import Path
from typing import List

import streamlit as st

from backend import ResourceItem


CSS_FILE = Path(__file__).parent / "static" / "styles.css"


def load_css() -> None:
    if CSS_FILE.exists():
        st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header() -> None:
    st.title("Acompanhamento de Metas")
    st.markdown(
        "<p class='subtitle'>Um painel de metas com árvore expansível, timeline, visualização de vídeos e PDFs em popups.</p>",
        unsafe_allow_html=True,
    )


def render_sidebar(summary: dict, weeks: List[str], metas: List[str], disciplines: List[str]) -> tuple[str, str, str]:
    st.sidebar.header("Filtros")
    selected_week = st.sidebar.selectbox("Semana", weeks)
    selected_meta = st.sidebar.selectbox("Meta", metas)
    selected_discipline = st.sidebar.selectbox("Disciplina", disciplines)

    st.sidebar.header("Visão geral")
    st.sidebar.metric("Itens", summary["resources"])
    st.sidebar.metric("Semanas", summary["weeks"])
    st.sidebar.metric("Metas", summary["metas"])
    st.sidebar.metric("Disciplinas", summary["disciplines"])
    st.sidebar.markdown(
        "<p class='sidebar-note'>Clique em um item para abrir o popup de visualização. Use a árvore para navegar por semanas, metas e disciplinas.</p>",
        unsafe_allow_html=True,
    )
    return selected_week, selected_meta, selected_discipline


def render_tree_panel(resources: List[ResourceItem]) -> None:
    st.subheader("Árvore de Metas")
    tree = {}
    for item in resources:
        tree.setdefault(item.week, {}).setdefault(item.meta, {}).setdefault(item.discipline, []).append(item)

    for week, metas in tree.items():
        with st.expander(f"{week}", expanded=False):
            for meta, disciplines in metas.items():
                with st.expander(f"{meta}", expanded=False):
                    for discipline, items in disciplines.items():
                        with st.expander(f"{discipline}", expanded=False):
                            for item in items:
                                status = "done" if item.completed else "pending"
                                st.markdown(
                                    f"<div class='tree-item {status}'>"
                                    f"<span class='tree-label'>{item.title}</span>"
                                    f"<span class='tree-meta'>{item.section}</span>"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )


def render_timeline_card(item: ResourceItem, selected: bool) -> None:
    if item.completed:
        card_class = "timeline-card done"
    elif item.type == "video":
        card_class = "timeline-card video"
    elif item.type == "pdf":
        card_class = "timeline-card pdf"
    else:
        card_class = "timeline-card file"

    active_class = " active" if selected else ""

    st.markdown(
        f"<div class='{card_class}{active_class}'>"
        f"<div class='card-top'>"
        f"<span class='card-badge'>{item.week} / {item.meta}</span>"
        f"<span class='card-type'>{item.type.upper()}</span>"
        f"</div>"
        f"<div class='card-title'>{item.title}</div>"
        f"<div class='card-desc'>{item.discipline} • {item.section}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_popup(item: ResourceItem, popup_html: str) -> None:
    st.markdown(
        f"<div class='popup-backdrop'>"
        f"<div class='popup-dialog'>"
        f"<div class='popup-header'>"
        f"<span class='popup-title'>{item.title}</span>"
        f"</div>"
        f"<div class='popup-body'>{popup_html}</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_status_bar(completed: int, total: int) -> None:
    st.progress(completed / total if total else 0)
    st.markdown(f"<p class='status-text'>**{completed}** de **{total}** itens concluídos.</p>", unsafe_allow_html=True)

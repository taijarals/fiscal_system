import pandas as pd
import requests
import streamlit as st

from pages.questoes import obter_config_supabase


TABLE = "fs_simulado_resultados"


def normalizar_resultado(item):
    return {
        "id": item.get("id"),
        "created_at": item.get("created_at"),
        "user_id": item.get("user_id"),
        "user_email": item.get("user_email"),
        "acertos": int(item.get("acertos", 0) or 0),
        "total_questoes": int(item.get("total_questoes", 0) or 0),
        "percentual": float(item.get("percentual", 0) or 0),
        "nao_respondidas": int(item.get("nao_respondidas", 0) or 0),
        "marcadas_para_revisao": int(item.get("marcadas_para_revisao", 0) or 0),
        "disciplina": item.get("disciplina"),
        "assunto": item.get("assunto"),
        "banca": item.get("banca"),
        "prova": item.get("prova"),
        "tipo_simulado": item.get("tipo_simulado"),
    }


def carregar_resultados():
    url, key = obter_config_supabase()

    if not (url and key):
        return [], "sem_config"

    token = st.session_state.get("auth_token")
    headers = {
        "apikey": key,
        "Content-Type": "application/json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = f"Bearer {key}"

    try:
        resposta = requests.get(
            f"{url}/rest/v1/{TABLE}",
            headers=headers,
            params={
                "select": "*",
                "order": "created_at.desc",
            },
            timeout=15,
        )
        resposta.raise_for_status()
        dados = resposta.json()
        return [normalizar_resultado(item) for item in dados], "supabase"
    except Exception as erro:
        st.warning(f"Não foi possível carregar os indicadores do Supabase: {erro}")
        return [], "erro"


def render():
    st.subheader("Indicadores")

    resultados, origem = carregar_resultados()

    usuario_atual = st.session_state.get("username") or st.session_state.get("auth_user", {}).get("email")
    if usuario_atual:
        resultados = [
            item
            for item in resultados
            if item.get("user_email") == usuario_atual or item.get("user_id") == usuario_atual
        ]

    if not resultados:
        st.info("Ainda não há dados de desempenho para este usuário.")
        if origem != "supabase":
            st.caption("Finalize alguns simulados para gerar métricas e visualizar seu progresso aqui.")
        return

    df = pd.DataFrame(resultados)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.sort_values("created_at").reset_index(drop=True)

    if df.empty:
        st.info("Ainda não há dados de desempenho para este usuário.")
        return

    total_simulados = len(df)
    media_percentual = round(df["percentual"].mean(), 1) if not df.empty else 0
    melhor_resultado = round(df["percentual"].max(), 1) if not df.empty else 0
    ultimo_resultado = round(df["percentual"].iloc[-1], 1) if not df.empty else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Simulados realizados", total_simulados)
    with col2:
        st.metric("Média de acerto", f"{media_percentual:.1f}%")
    with col3:
        st.metric("Melhor resultado", f"{melhor_resultado:.1f}%")
    with col4:
        st.metric("Último resultado", f"{ultimo_resultado:.1f}%")

    st.divider()

    view = st.radio(
        "Visualizar por",
        ["Tempo", "Disciplina", "Assunto"],
        horizontal=True,
        key="indicadores_view",
    )

    if view == "Tempo":
        evolucao = df[["created_at", "percentual"]].dropna()
        if not evolucao.empty:
            st.markdown("### Evolução ao longo do tempo")
            st.line_chart(evolucao.set_index("created_at")["percentual"], use_container_width=True)
    elif view == "Disciplina":
        if "disciplina" in df.columns:
            disciplinas = sorted([valor for valor in df["disciplina"].dropna().astype(str).unique() if valor])
            disciplina_selecionada = st.selectbox(
                "Selecione uma disciplina",
                ["Todas"] + disciplinas,
                key="indicador_disciplina",
            )
            dados_filtrados = df if disciplina_selecionada == "Todas" else df[df["disciplina"].astype(str) == disciplina_selecionada]

            desempenho_por_disciplina = (
                dados_filtrados.groupby("disciplina")["percentual"]
                .mean()
                .reset_index()
                .dropna()
            )
            if not desempenho_por_disciplina.empty:
                st.markdown(f"### Desempenho por disciplina{f' - {disciplina_selecionada}' if disciplina_selecionada != 'Todas' else ''}")
                st.bar_chart(
                    desempenho_por_disciplina.set_index("disciplina")["percentual"],
                    use_container_width=True,
                )
            else:
                st.info("Não há dados suficientes para agrupar por disciplina.")
    else:
        if "assunto" in df.columns:
            assuntos = sorted([valor for valor in df["assunto"].dropna().astype(str).unique() if valor])
            assunto_selecionado = st.selectbox(
                "Selecione um assunto",
                ["Todos"] + assuntos,
                key="indicador_assunto",
            )
            dados_filtrados = df if assunto_selecionado == "Todos" else df[df["assunto"].astype(str) == assunto_selecionado]

            desempenho_por_assunto = (
                dados_filtrados.groupby("assunto")["percentual"]
                .mean()
                .reset_index()
                .dropna()
            )
            if not desempenho_por_assunto.empty:
                st.markdown(f"### Desempenho por assunto{f' - {assunto_selecionado}' if assunto_selecionado != 'Todos' else ''}")
                st.bar_chart(
                    desempenho_por_assunto.set_index("assunto")["percentual"],
                    use_container_width=True,
                )
            else:
                st.info("Não há dados suficientes para agrupar por assunto.")

    st.divider()

    st.markdown("### Últimos simulados")
    tabela = df[[
        "created_at",
        "acertos",
        "total_questoes",
        "percentual",
        "disciplina",
        "assunto",
        "banca",
        "prova",
    ]].copy()
    tabela["created_at"] = tabela["created_at"].dt.strftime("%d/%m/%Y %H:%M")
    st.dataframe(tabela.sort_values("created_at", ascending=False).head(10), use_container_width=True, hide_index=True)

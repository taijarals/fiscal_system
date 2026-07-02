import pandas as pd
import requests
import streamlit as st

from pages.questoes import obter_config_supabase


TABELA_QUESTOES = "fs_questoes_resultados"
TABELA_SIMULADO = "fs_simulado_resultados"


def obter_headers():
    url, key = obter_config_supabase()

    if not (url and key):
        return None, None, None

    token = st.session_state.get("auth_token")
    headers = {
        "apikey": key,
        "Content-Type": "application/json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = f"Bearer {key}"

    return url, key, headers


def obter_identificadores_usuario():
    auth_user = st.session_state.get("auth_user", {}) or {}
    usuario = st.session_state.get("username")

    user_id = auth_user.get("id") or usuario
    user_email = auth_user.get("email") or (usuario if usuario and "@" in usuario else None)

    return user_id, user_email


def normalizar_resultado(item):
    acertou = item.get("acertou")
    if isinstance(acertou, str):
        acertou = acertou.strip().lower() in {"true", "1", "sim", "s", "yes", "y"}

    if acertou is None:
        percentual = item.get("percentual")
        percentual = float(percentual) if percentual not in (None, "") else None
    elif acertou:
        percentual = float(item.get("percentual", 100) or 100)
    else:
        percentual = float(item.get("percentual", 0) or 0)

    return {
        "id": item.get("id"),
        "created_at": item.get("created_at"),
        "user_id": item.get("user_id"),
        "user_email": item.get("user_email"),
        "acertou": acertou,
        "percentual": percentual,
        "marcada_para_revisao": bool(item.get("marcada_para_revisao", False)),
        "disciplina": item.get("disciplina"),
        "assunto": item.get("assunto"),
        "banca": item.get("banca"),
        "prova": item.get("prova"),
        "tipo_questao": item.get("tipo_questao"),
        "codigo": item.get("codigo"),
        "resposta": item.get("resposta"),
        "alternativa_certa": item.get("alternativa_certa"),
        "tipo_simulado": item.get("tipo_simulado"),
    }


def carregar_resultados():
    url, _, headers = obter_headers()

    if not (url and headers):
        return [], "sem_config"

    resultados = []
    origem = None

    for tabela in [TABELA_QUESTOES, TABELA_SIMULADO]:
        try:
            resposta = requests.get(
                f"{url}/rest/v1/{tabela}",
                headers=headers,
                params={
                    "select": "*",
                    "order": "created_at.desc",
                },
                timeout=15,
            )
            resposta.raise_for_status()
            dados = resposta.json()
            if dados:
                resultados.extend(normalizar_resultado(item) for item in dados)
                origem = tabela if origem is None else "ambas"
        except Exception as erro:
            st.warning(f"Não foi possível carregar os indicadores do Supabase em {tabela}: {erro}")

    if not resultados:
        return [], origem or "sem_dados"

    return resultados, origem


def deletar_todos_resultados():
    url, _, headers = obter_headers()
    user_id, user_email = obter_identificadores_usuario()

    if not (url and headers):
        return {"total": 0, "tabelas": {}, "erro": "sem_config"}

    if not (user_id or user_email):
        return {"total": 0, "tabelas": {}, "erro": "sem_usuario"}

    filtros = {"select": "id"}
    filtros_or = []
    if user_email:
        filtros_or.append(f"user_email.eq.{user_email}")
    if user_id:
        filtros_or.append(f"user_id.eq.{user_id}")
    if filtros_or:
        filtros["or"] = ",".join(filtros_or)

    detalhes = {}
    total = 0

    for tabela in [TABELA_QUESTOES, TABELA_SIMULADO]:
        try:
            resposta = requests.get(
                f"{url}/rest/v1/{tabela}",
                headers=headers,
                params=filtros,
                timeout=15,
            )
            resposta.raise_for_status()
            ids = [item["id"] for item in resposta.json() if item.get("id") is not None]

            for identificador in ids:
                delete_resposta = requests.delete(
                    f"{url}/rest/v1/{tabela}",
                    headers=headers,
                    params={"id": f"eq.{identificador}"},
                    timeout=15,
                )
                delete_resposta.raise_for_status()

            detalhes[tabela] = len(ids)
            total += len(ids)
        except Exception as erro:
            detalhes[tabela] = f"erro: {erro}"

    return {"total": total, "tabelas": detalhes}


def render():
    st.subheader("Indicadores")

    resultados, origem = carregar_resultados()

    user_id, user_email = obter_identificadores_usuario()
    if user_id or user_email:
        resultados = [
            item
            for item in resultados
            if (user_id and item.get("user_id") == user_id)
            or (user_email and item.get("user_email") == user_email)
        ]

    with st.expander("Limpar dados de resultados", expanded=False):
        st.warning(
            "Esta ação remove apenas os registros deste usuário nas tabelas fs_questoes_resultados e fs_simulado_resultados."
        )
        if st.button("Excluir meus registros", type="secondary"):
            resultado_limpeza = deletar_todos_resultados()
            if resultado_limpeza.get("erro") == "sem_config":
                st.error("Configure o Supabase para limpar os dados automaticamente.")
            elif resultado_limpeza.get("erro") == "sem_usuario":
                st.error("Não foi possível identificar o usuário atual para exclusão.")
            else:
                st.success(
                    f"Registros removidos: {resultado_limpeza.get('total', 0)}."
                )
                st.rerun()

    if not resultados:
        st.info("Ainda não há dados de desempenho para este usuário.")
        if origem != "sem_config":
            st.caption("Finalize alguns simulados para gerar métricas e visualizar seu progresso aqui.")
        return

    df = pd.DataFrame(resultados)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.sort_values("created_at").reset_index(drop=True)

    if df.empty:
        st.info("Ainda não há dados de desempenho para este usuário.")
        return

    percentuais_validos = df["percentual"].dropna()
    total_questoes = len(df)
    acertos = int(df["acertou"].fillna(False).sum()) if "acertou" in df.columns else 0
    media_percentual = round(percentuais_validos.mean(), 1) if not percentuais_validos.empty else 0
    melhor_resultado = round(percentuais_validos.max(), 1) if not percentuais_validos.empty else 0
    ultimo_resultado = round(percentuais_validos.iloc[-1], 1) if not percentuais_validos.empty else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Questões respondidas", total_questoes)
    with col2:
        st.metric("Acertos", acertos)
    with col3:
        st.metric("Taxa de acerto", f"{media_percentual:.1f}%")
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
            st.line_chart(evolucao.set_index("created_at")["percentual"], width='stretch')
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
                    width='stretch',
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
                    width='stretch',
                )
            else:
                st.info("Não há dados suficientes para agrupar por assunto.")

    st.divider()

    st.markdown("### Últimas questões respondidas")
    tabela = df[[
        "created_at",
        "codigo",
        "disciplina",
        "assunto",
        "banca",
        "prova",
        "acertou",
        "percentual",
        "resposta",
        "marcada_para_revisao",
    ]].copy()
    tabela["created_at"] = tabela["created_at"].dt.strftime("%d/%m/%Y %H:%M")
    st.dataframe(tabela.sort_values("created_at", ascending=False).head(20), width='stretch', hide_index=True)

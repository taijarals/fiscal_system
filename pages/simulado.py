from copy import deepcopy
import random

import pandas as pd
import streamlit as st

from pages.questoes import (
    inicializar_questoes,
    opcoes_filtro,
    aplicar_filtros,
    normalizar_questao,
)


def inicializar_simulado_state():
    """Inicializa o estado do simulado na sessão."""
    if "simulado_iniciado" not in st.session_state:
        st.session_state.simulado_iniciado = False
        st.session_state.simulado_questoes = []
        st.session_state.simulado_respostas = {}
        st.session_state.simulado_indice = 0
        st.session_state.simulado_finalizado = False


def selecionar_questoes_simulado(questoes, numero_questoes):
    """Seleciona aleatoriamente questões para o simulado."""
    if len(questoes) < numero_questoes:
        st.warning(f"Apenas {len(questoes)} questão(ões) disponível(is).")
        numero_questoes = len(questoes)
    
    questoes_selecionadas = random.sample(questoes, numero_questoes)
    return questoes_selecionadas


def iniciar_simulado(questoes_selecionadas):
    """Inicia um novo simulado."""
    st.session_state.simulado_iniciado = True
    st.session_state.simulado_questoes = questoes_selecionadas
    st.session_state.simulado_respostas = {
        i: {"resposta": "", "marcada_para_revisao": False}
        for i in range(len(questoes_selecionadas))
    }
    st.session_state.simulado_indice = 0
    st.session_state.simulado_finalizado = False


def finalizar_simulado():
    """Finaliza o simulado e calcula o resultado."""
    st.session_state.simulado_finalizado = True


def obter_questao_atual():
    """Retorna a questão atual do simulado."""
    if st.session_state.simulado_indice < len(st.session_state.simulado_questoes):
        return st.session_state.simulado_questoes[st.session_state.simulado_indice]
    return None


def calcular_resultado():
    """Calcula o resultado do simulado."""
    questoes = st.session_state.simulado_questoes
    respostas = st.session_state.simulado_respostas
    
    acertos = 0
    total = len(questoes)
    
    for i, questao in enumerate(questoes):
        if questao["tipo_questao"] == "Múltipla escolha":
            if respostas[i]["resposta"] == questao["alternativa_certa"]:
                acertos += 1
    
    percentual = (acertos / total * 100) if total > 0 else 0
    return acertos, total, percentual


def render_selecao_simulado():
    """Renderiza a tela de seleção de questões para o simulado."""
    st.subheader("Novo Simulado")
    
    inicializar_questoes()
    df = pd.DataFrame(st.session_state.questoes)
    
    col1, col2 = st.columns(2)
    
    with col1:
        disciplina = st.selectbox(
            "Filtrar por disciplina",
            opcoes_filtro(df, "disciplina", "Todas")
        )
        banca = st.selectbox(
            "Filtrar por banca",
            opcoes_filtro(df, "banca", "Todas")
        )
        ano = st.selectbox(
            "Filtrar por ano",
            opcoes_filtro(df, "ano", "Todos")
        )
    
    with col2:
        assunto = st.selectbox(
            "Filtrar por assunto",
            opcoes_filtro(df, "assunto", "Todos")
        )
        prova = st.selectbox(
            "Filtrar por prova",
            opcoes_filtro(df, "prova", "Todas")
        )
    
    df_filtrado = aplicar_filtros(
        df, disciplina, assunto, ano, banca, prova, "Todos", ""
    )
    
    st.info(f"**{len(df_filtrado)}** questão(ões) disponível(is) com os filtros aplicados.")
    
    numero_questoes = st.slider(
        "Quantas questões deseja resolver?",
        min_value=1,
        max_value=max(1, len(df_filtrado)),
        value=min(10, max(1, len(df_filtrado))),
    )
    
    if st.button("Iniciar Simulado", width='stretch', type='primary'):
        questoes_lista = df_filtrado.to_dict('records')
        questoes_selecionadas = selecionar_questoes_simulado(questoes_lista, numero_questoes)
        iniciar_simulado(questoes_selecionadas)
        st.rerun()


def render_questao_simulado():
    """Renderiza a questão atual do simulado."""
    questao = obter_questao_atual()
    if questao is None:
        return
    
    indice_atual = st.session_state.simulado_indice
    total_questoes = len(st.session_state.simulado_questoes)
    resposta_atual = st.session_state.simulado_respostas[indice_atual]
    
    # Header com progresso
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Questão {indice_atual + 1} de {total_questoes}")
    with col2:
        if st.checkbox(
            "Marcar para revisão",
            value=resposta_atual["marcada_para_revisao"],
            key=f"revisao_{indice_atual}"
        ):
            st.session_state.simulado_respostas[indice_atual]["marcada_para_revisao"] = True
        else:
            st.session_state.simulado_respostas[indice_atual]["marcada_para_revisao"] = False
    
    st.divider()
    
    # Informações da questão
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"**Disciplina:** {questao['disciplina']}")
    with col2:
        st.caption(f"**Assunto:** {questao['assunto'] or 'N/A'}")
    with col3:
        st.caption(f"**Banca:** {questao['banca'] or 'N/A'}")
    
    st.divider()
    
    # Enunciado
    st.markdown(f"**Enunciado:**\n\n{questao['enunciado']}")
    
    st.divider()
    
    # Respostas
    if questao["tipo_questao"] == "Múltipla escolha":
        st.markdown("**Alternativas:**")
        
        alternativas = {
            "A": questao["alternativa_a"],
            "B": questao["alternativa_b"],
            "C": questao["alternativa_c"],
            "D": questao["alternativa_d"],
            "E": questao["alternativa_e"],
        }
        
        resposta_marcada = st.radio(
            "Selecione uma alternativa:",
            options=list(alternativas.keys()),
            format_func=lambda x: f"{x} - {alternativas[x]}",
            index=None if resposta_atual["resposta"] == "" else list(alternativas.keys()).index(resposta_atual["resposta"]),
            key=f"resposta_{indice_atual}"
        )
        
        if resposta_marcada:
            st.session_state.simulado_respostas[indice_atual]["resposta"] = resposta_marcada
    
    else:  # Questão aberta
        st.markdown("**Sua Resposta:**")
        resposta_texto = st.text_area(
            "Digite sua resposta",
            value=resposta_atual["resposta"],
            height=100,
            key=f"resposta_aberta_{indice_atual}",
            label_visibility="collapsed"
        )
        st.session_state.simulado_respostas[indice_atual]["resposta"] = resposta_texto
    
    st.divider()
    
    # Navegação
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("← Anterior", width='stretch', disabled=(indice_atual == 0)):
            st.session_state.simulado_indice -= 1
            st.rerun()
    
    with col2:
        if st.button("Próxima →", width='stretch', disabled=(indice_atual == total_questoes - 1)):
            st.session_state.simulado_indice += 1
            st.rerun()
    
    with col3:
        if st.button("Saltar para", width='stretch'):
            pass
    
    with col4:
        if st.button("Finalizar", width='stretch', type='primary'):
            finalizar_simulado()
            st.rerun()


def render_resultado_simulado():
    """Renderiza o resultado do simulado."""
    st.subheader("Resultado do Simulado")
    
    acertos, total, percentual = calcular_resultado()
    
    # Card de resultado
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Acertos", f"{acertos}/{total}")
    with col2:
        st.metric("Percentual", f"{percentual:.1f}%")
    with col3:
        total_revisao = sum(
            1 for r in st.session_state.simulado_respostas.values()
            if r["marcada_para_revisao"]
        )
        st.metric("Marcadas para Revisão", total_revisao)
    with col4:
        total_nao_respondidas = sum(
            1 for r in st.session_state.simulado_respostas.values()
            if r["resposta"] == ""
        )
        st.metric("Não Respondidas", total_nao_respondidas)
    
    st.divider()
    
    # Análise de respostas
    st.subheader("Análise de Respostas")
    
    tabs = st.tabs(["Todas as Respostas", "Apenas Erros", "Marcadas para Revisão"])
    
    with tabs[0]:
        render_analise_respostas("todas")
    
    with tabs[1]:
        render_analise_respostas("erros")
    
    with tabs[2]:
        render_analise_respostas("revisao")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Novo Simulado", width='stretch', type='primary'):
            st.session_state.simulado_iniciado = False
            st.session_state.simulado_finalizado = False
            st.rerun()
    
    with col2:
        if st.button("Voltar", width='stretch'):
            st.session_state.simulado_iniciado = False
            st.session_state.simulado_finalizado = False
            st.rerun()


def render_analise_respostas(tipo_filtro):
    """Renderiza a análise de respostas."""
    questoes = st.session_state.simulado_questoes
    respostas = st.session_state.simulado_respostas
    
    for i, questao in enumerate(questoes):
        resposta = respostas[i]
        
        # Aplicar filtros
        if tipo_filtro == "erros":
            if questao["tipo_questao"] != "Múltipla escolha":
                continue
            if resposta["resposta"] == questao["alternativa_certa"]:
                continue
        
        elif tipo_filtro == "revisao":
            if not resposta["marcada_para_revisao"]:
                continue
        
        # Mostrar questão
        with st.expander(
            f"Questão {i + 1} - {questao['codigo']} "
            f"({questao['disciplina']} - {questao['assunto']})"
        ):
            st.markdown(f"**Enunciado:**\n\n{questao['enunciado']}")
            
            if questao["tipo_questao"] == "Múltipla escolha":
                alternativas = {
                    "A": questao["alternativa_a"],
                    "B": questao["alternativa_b"],
                    "C": questao["alternativa_c"],
                    "D": questao["alternativa_d"],
                    "E": questao["alternativa_e"],
                }
                
                col1, col2 = st.columns(2)
                
                with col1:
                    resposta_marcada = resposta["resposta"]
                    status = "✅" if resposta_marcada == questao["alternativa_certa"] else "❌"
                    st.markdown(f"**Sua resposta:** {status}\n\n**{resposta_marcada}** - {alternativas.get(resposta_marcada, 'Não respondida')}")
                
                with col2:
                    st.markdown(f"**Resposta correta:**\n\n**{questao['alternativa_certa']}** - {alternativas[questao['alternativa_certa']]}")
            
            else:  # Aberta
                st.markdown(f"**Sua resposta:**\n\n{resposta['resposta'] or '*Não respondida*'}")
                st.markdown(f"**Gabarito:**\n\n{questao['gabarito_aberta']}")
            
            if questao["comentario_ia"]:
                st.info(f"💡 **Comentário:** {questao['comentario_ia']}")


def render():
    """Renderiza a página de simulados."""
    inicializar_questoes()
    inicializar_simulado_state()
    
    if not st.session_state.simulado_iniciado:
        render_selecao_simulado()
    
    elif st.session_state.simulado_finalizado:
        render_resultado_simulado()
    
    else:
        render_questao_simulado()

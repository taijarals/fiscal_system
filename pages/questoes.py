from copy import deepcopy
import json

import pandas as pd
import requests
import streamlit as st


SUPABASE_TABLE = "fs_questoes"
TIPOS_QUESTAO = ["Múltipla escolha", "Aberta"]
ALTERNATIVAS = ["A", "B", "C", "D", "E"]
COLUNAS_LISTAGEM = [
    "id_questao",
    "codigo",
    "disciplina",
    "assunto",
    "ano",
    "banca",
    "prova",
    "tipo_questao",
    "alternativa_certa",
]

CAMPOS_QUESTAO = [
    "id_questao",
    "codigo",
    "disciplina",
    "assunto",
    "ano",
    "banca",
    "prova",
    "enunciado",
    "alternativa_a",
    "alternativa_b",
    "alternativa_c",
    "alternativa_d",
    "alternativa_e",
    "alternativa_certa",
    "comentario_ia",
    "tipo_questao",
    "gabarito_aberta",
]

QUESTOES_INICIAIS = [
    {
        "id_questao": None,
        "codigo": 1,
        "disciplina": "ICMS",
        "assunto": "Crédito Fiscal",
        "ano": 2024,
        "banca": "Exemplo",
        "prova": "SEFAZ BA",
        "enunciado": "Qual a alíquota interna da Bahia?",
        "alternativa_a": "7%",
        "alternativa_b": "20,5%",
        "alternativa_c": "12%",
        "alternativa_d": "18%",
        "alternativa_e": "25%",
        "alternativa_certa": "B",
        "comentario_ia": "Verifique a legislação estadual vigente para confirmar a alíquota aplicável.",
        "tipo_questao": "Múltipla escolha",
        "gabarito_aberta": "",
    },
    {
        "id_questao": None,
        "codigo": 2,
        "disciplina": "IPI",
        "assunto": "Industrialização",
        "ano": 2023,
        "banca": "Exemplo",
        "prova": "Receita Federal",
        "enunciado": "Explique o que caracteriza industrialização para fins de IPI.",
        "alternativa_a": "",
        "alternativa_b": "",
        "alternativa_c": "",
        "alternativa_d": "",
        "alternativa_e": "",
        "alternativa_certa": "",
        "comentario_ia": "A resposta deve abordar transformação, beneficiamento, montagem, acondicionamento ou renovação.",
        "tipo_questao": "Aberta",
        "gabarito_aberta": "Industrialização é qualquer operação que modifique natureza, funcionamento, acabamento, apresentação ou finalidade do produto.",
    },
]


def normalizar_questao(questao):
    return {
        "id_questao": questao.get("id_questao"),
        "codigo": questao.get("codigo", questao.get("id", 0)),
        "disciplina": questao.get("disciplina", ""),
        "assunto": questao.get("assunto", ""),
        "ano": questao.get("ano"),
        "banca": questao.get("banca", ""),
        "prova": questao.get("prova", questao.get("titulo", "")),
        "enunciado": questao.get("enunciado", ""),
        "alternativa_a": questao.get("alternativa_a", ""),
        "alternativa_b": questao.get("alternativa_b", ""),
        "alternativa_c": questao.get("alternativa_c", ""),
        "alternativa_d": questao.get("alternativa_d", ""),
        "alternativa_e": questao.get("alternativa_e", ""),
        "alternativa_certa": questao.get("alternativa_certa", questao.get("correta", "")),
        "comentario_ia": questao.get("comentario_ia", ""),
        "tipo_questao": questao.get("tipo_questao", "Múltipla escolha"),
        "gabarito_aberta": questao.get("gabarito_aberta", ""),
    }


def preparar_questao_supabase(questao):
    questao_normalizada = normalizar_questao(questao)
    return {
        campo: questao_normalizada[campo]
        for campo in CAMPOS_QUESTAO
        if campo != "id_questao"
    }


def obter_config_supabase():
    try:
        secao_supabase = st.secrets.get("supabase", {})
        url = st.secrets.get("SUPABASE_URL") or secao_supabase.get("url")
        key = st.secrets.get("SUPABASE_KEY") or secao_supabase.get("key")
    except Exception:
        return None, None

    return url, key


def supabase_configurado():
    url, key = obter_config_supabase()
    return bool(url and key), url, key


def listar_questoes_supabase():
    configurado, url, key = supabase_configurado()

    if not configurado:
        return None

    resposta = requests.get(
        f"{url}/rest/v1/{SUPABASE_TABLE}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
        },
        params={
            "select": "*",
            "order": "id_questao.asc",
        },
        timeout=15,
    )
    resposta.raise_for_status()
    return [normalizar_questao(questao) for questao in resposta.json()]


def inserir_questao_supabase(questao):
    configurado, url, key = supabase_configurado()

    if not configurado:
        return False

    resposta = requests.post(
        f"{url}/rest/v1/{SUPABASE_TABLE}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=preparar_questao_supabase(questao),
        timeout=15,
    )
    resposta.raise_for_status()
    dados = resposta.json()

    if dados:
        return normalizar_questao(dados[0])

    return normalizar_questao(questao)


def carregar_questoes():
    try:
        questoes_supabase = listar_questoes_supabase()
    except Exception as erro:
        st.error(f"Não foi possível carregar as questões do Supabase: {erro}")
        return deepcopy(QUESTOES_INICIAIS), "erro"

    if questoes_supabase is None:
        st.warning(
            "Supabase não configurado. Cadastre SUPABASE_URL e SUPABASE_KEY em .streamlit/secrets.toml."
        )
        return deepcopy(QUESTOES_INICIAIS), "local"

    return questoes_supabase, "supabase"


def inicializar_questoes(forcar_recarregamento=False):
    if forcar_recarregamento or "questoes" not in st.session_state:
        questoes, origem = carregar_questoes()
        st.session_state.questoes = questoes
        st.session_state.origem_questoes = origem
    else:
        st.session_state.questoes = [
            normalizar_questao(questao) for questao in st.session_state.questoes
        ]


def opcoes_filtro(df, coluna, opcao_padrao):
    if df.empty or coluna not in df.columns:
        return [opcao_padrao]

    opcoes = sorted(df[coluna].dropna().astype(str).unique())
    return [opcao_padrao] + opcoes


def aplicar_filtros(df, disciplina, assunto, ano, banca, prova, tipo_questao, pesquisa):
    df_filtrado = df.copy()

    if disciplina != "Todas":
        df_filtrado = df_filtrado[df_filtrado["disciplina"].astype(str) == disciplina]

    if assunto != "Todos":
        df_filtrado = df_filtrado[df_filtrado["assunto"].astype(str) == assunto]

    if ano != "Todos":
        df_filtrado = df_filtrado[df_filtrado["ano"].astype(str) == ano]

    if banca != "Todas":
        df_filtrado = df_filtrado[df_filtrado["banca"].astype(str) == banca]

    if prova != "Todas":
        df_filtrado = df_filtrado[df_filtrado["prova"].astype(str) == prova]

    if tipo_questao != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo_questao"].astype(str) == tipo_questao]

    if pesquisa:
        texto = pesquisa.strip().lower()
        colunas_pesquisa = [
            "disciplina",
            "assunto",
            "banca",
            "prova",
            "enunciado",
            "comentario_ia",
            "gabarito_aberta",
        ]
        mascara = df_filtrado[colunas_pesquisa].apply(
            lambda coluna: coluna.astype(str).str.lower().str.contains(texto, na=False)
        ).any(axis=1)
        df_filtrado = df_filtrado[mascara]

    return df_filtrado


def validar_questao(tipo_questao, campos):
    campos_obrigatorios = [
        "codigo",
        "disciplina",
        "enunciado",
        "tipo_questao",
    ]

    for campo in campos_obrigatorios:
        if not str(campos[campo]).strip():
            return False, "Preencha os campos obrigatórios da questão."

    if tipo_questao == "Múltipla escolha":
        alternativas_obrigatorias = [
            "alternativa_a",
            "alternativa_b",
            "alternativa_c",
            "alternativa_d",
            "alternativa_e",
        ]
        for campo in alternativas_obrigatorias:
            if not campos[campo].strip():
                return False, "Preencha todas as alternativas da questão de múltipla escolha."

        if not campos["alternativa_certa"].strip():
            return False, "Selecione a alternativa certa da questão."

    if tipo_questao == "Aberta" and not campos["gabarito_aberta"].strip():
        return False, "Preencha o gabarito da questão aberta."

    return True, ""


def proximo_codigo():
    codigos = [int(q["codigo"]) for q in st.session_state.questoes if q.get("codigo")]
    return max(codigos, default=0) + 1


def salvar_questao(questao):
    questao_salva = inserir_questao_supabase(questao)

    if questao_salva:
        st.session_state.questoes.append(questao_salva)
        st.session_state.origem_questoes = "supabase"
        return

    st.session_state.questoes.append(questao)
    st.session_state.origem_questoes = "local"


def carregar_questoes_json(arquivo_json):
    try:
        dados = json.load(arquivo_json)
    except Exception as erro:
        raise ValueError(f"Arquivo JSON inválido: {erro}")

    if isinstance(dados, dict):
        if "questoes" in dados:
            questoes = dados["questoes"]
        elif "questions" in dados:
            questoes = dados["questions"]
        else:
            raise ValueError(
                "JSON deve conter uma lista de questões ou um objeto com a chave 'questoes'."
            )
    elif isinstance(dados, list):
        questoes = dados
    else:
        raise ValueError(
            "Formato JSON inválido. Use uma lista de questões ou um objeto com a chave 'questoes'."
        )

    if not isinstance(questoes, list):
        raise ValueError("A chave 'questoes' deve conter uma lista de questões.")

    return questoes


def importar_questoes_lote(arquivo_json):
    questoes = carregar_questoes_json(arquivo_json)
    if not questoes:
        raise ValueError("Nenhuma questão encontrada no arquivo JSON.")

    novas_questoes = []
    for questao in questoes:
        questao_normalizada = normalizar_questao(questao)

        if not questao_normalizada.get("codigo"):
            questao_normalizada["codigo"] = proximo_codigo()

        valido, mensagem = validar_questao(
            questao_normalizada["tipo_questao"], questao_normalizada
        )
        if not valido:
            raise ValueError(
                f"Erro na questão {questao_normalizada.get('codigo', 'sem código')}: {mensagem}"
            )

        novas_questoes.append(questao_normalizada)

    for questao in novas_questoes:
        salvar_questao(questao)

    return len(novas_questoes)


def render_formulario_nova_questao():
    @st.dialog("Nova Questão")
    def formulario():
        with st.form("nova_questao"):
            col1, col2 = st.columns(2)

            with col1:
                codigo = st.number_input(
                    "Código",
                    min_value=1,
                    step=1,
                    value=proximo_codigo(),
                )
                disciplina = st.text_input("Disciplina")
                assunto = st.text_input("Assunto")
                banca = st.text_input("Banca")

            with col2:
                ano = st.number_input("Ano", min_value=1900, max_value=2100, step=1, value=2026)
                prova = st.text_input("Prova")
                tipo_questao = st.selectbox("Tipo de Questão", TIPOS_QUESTAO)

            enunciado = st.text_area("Enunciado")

            alternativa_a = ""
            alternativa_b = ""
            alternativa_c = ""
            alternativa_d = ""
            alternativa_e = ""
            alternativa_certa = ""
            gabarito_aberta = ""

            if tipo_questao == "Múltipla escolha":
                with st.expander("Alternativas", expanded=True):
                    alternativa_a = st.text_area("Alternativa A")
                    alternativa_b = st.text_area("Alternativa B")
                    alternativa_c = st.text_area("Alternativa C")
                    alternativa_d = st.text_area("Alternativa D")
                    alternativa_e = st.text_area("Alternativa E")
                    alternativa_certa = st.selectbox("Alternativa Certa", ALTERNATIVAS)
            else:
                with st.expander("Gabarito da Questão Aberta", expanded=True):
                    gabarito_aberta = st.text_area("Gabarito")

            comentario_ia = st.text_area("Comentário IA")

            salvar = st.form_submit_button("Salvar", width='stretch')

            if salvar:
                campos = {
                    "codigo": codigo,
                    "disciplina": disciplina,
                    "enunciado": enunciado,
                    "tipo_questao": tipo_questao,
                    "alternativa_a": alternativa_a,
                    "alternativa_b": alternativa_b,
                    "alternativa_c": alternativa_c,
                    "alternativa_d": alternativa_d,
                    "alternativa_e": alternativa_e,
                    "alternativa_certa": alternativa_certa,
                    "gabarito_aberta": gabarito_aberta,
                }
                valido, mensagem = validar_questao(tipo_questao, campos)

                if not valido:
                    st.error(mensagem)
                    return

                questao = {
                    "id_questao": None,
                    "codigo": int(codigo),
                    "disciplina": disciplina.strip(),
                    "assunto": assunto.strip() or None,
                    "ano": int(ano) if ano else None,
                    "banca": banca.strip() or None,
                    "prova": prova.strip() or None,
                    "enunciado": enunciado.strip(),
                    "alternativa_a": alternativa_a.strip() or None,
                    "alternativa_b": alternativa_b.strip() or None,
                    "alternativa_c": alternativa_c.strip() or None,
                    "alternativa_d": alternativa_d.strip() or None,
                    "alternativa_e": alternativa_e.strip() or None,
                    "alternativa_certa": alternativa_certa or None,
                    "comentario_ia": comentario_ia.strip() or None,
                    "tipo_questao": tipo_questao,
                    "gabarito_aberta": gabarito_aberta.strip() or None,
                }

                try:
                    salvar_questao(questao)
                except Exception as erro:
                    st.error(f"Não foi possível salvar a questão no Supabase: {erro}")
                    return

                st.rerun()

    formulario()


def render():
    inicializar_questoes()

    # ==================================================
    # TOOLBAR
    # ==================================================

    col1, col2, col3 = st.columns([7, 2, 2])

    with col1:
        st.subheader("Questões")

    with col2:
        nova_questao = st.button("Nova Questão", width='stretch')

    with col3:
        recarregar = st.button("Recarregar", width='stretch')

    if recarregar:
        inicializar_questoes(forcar_recarregamento=True)
        st.rerun()

    with st.expander("Importar questões em lote", expanded=False):
        with st.form("importar_questoes_lote"):
            arquivo_json = st.file_uploader(
                "Selecione um arquivo JSON",
                type=["json"],
                help="O JSON deve conter uma lista de questões ou um objeto com a chave 'questoes'.",
            )
            importar_lote = st.form_submit_button(
                "Importar questões em lote",
                width='stretch',
            )

            if importar_lote:
                if not arquivo_json:
                    st.error("Selecione um arquivo JSON antes de importar.")
                else:
                    try:
                        quantidade = importar_questoes_lote(arquivo_json)
                        st.success(f"{quantidade} questão(ões) importada(s) com sucesso.")
                        st.rerun()
                    except Exception as erro:
                        st.error(f"Não foi possível importar o lote: {erro}")

    if st.session_state.get("origem_questoes") == "supabase":
        st.caption("Dados carregados do Supabase.")
    else:
        st.caption("Dados locais de exemplo em uso.")

    st.divider()

    df = pd.DataFrame(st.session_state.questoes, columns=CAMPOS_QUESTAO)

    # ==================================================
    # FILTROS
    # ==================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        disciplina = st.selectbox("Disciplina", opcoes_filtro(df, "disciplina", "Todas"))
        banca = st.selectbox("Banca", opcoes_filtro(df, "banca", "Todas"))

    with col2:
        assunto = st.selectbox("Assunto", opcoes_filtro(df, "assunto", "Todos"))
        prova = st.selectbox("Prova", opcoes_filtro(df, "prova", "Todas"))

    with col3:
        ano = st.selectbox("Ano", opcoes_filtro(df, "ano", "Todos"))
        tipo_questao = st.selectbox("Tipo", ["Todos"] + TIPOS_QUESTAO)

    pesquisa = st.text_input("Pesquisar")

    st.divider()

    # ==================================================
    # TABELA
    # ==================================================

    df_filtrado = aplicar_filtros(df, disciplina, assunto, ano, banca, prova, tipo_questao, pesquisa)

    st.dataframe(
        df_filtrado[COLUNAS_LISTAGEM],
        width='stretch',
        hide_index=True,
    )

    st.caption(f"{len(df_filtrado)} questão(ões) encontrada(s).")

    # ==================================================
    # FORMULÁRIO
    # ==================================================

    if nova_questao:
        render_formulario_nova_questao()

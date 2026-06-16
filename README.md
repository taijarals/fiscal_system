# fiscal_system

Aplicação Streamlit para acompanhar metas e progresso em `attachments/`.

## Como executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o app:
   ```bash
   streamlit run app.py
   ```

## O que o app faz

- Escaneia automaticamente a pasta `attachments/`.
- Exibe progresso geral e progresso por meta.
- Permite marcar arquivos como concluídos.
- Salva o progresso em `tracking_state.json`.

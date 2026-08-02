# SOSO

## 1. Stack:

- Frontend/Backend: Streamlit
- Banco de Dados: PostgreSQL (Supabase) via SQLAlchemy e psycopg2-binary
-  Manipulação de Dados: Pandas / Openpyxl

## 2. Requisitos do Sistema:

- Banco de Dados: Tabelas para categorias, gastos_fixos e lancamentos (receitas, despesas sazonais/variáveis, investimentos).
- Script de Migração (migrar.py): Ler uma planilha Excel local (financas.xlsx), tratar os dados com Pandas e popular o banco no Supabase.
- Aplicação Principal (app.py):

## 3. Tela

- Dashboard: Visão mês a mês de Total Ganho, Total Gasto e Total Investido, com gráficos simples (Plotly).
- Novo Lançamento: Formulário simples para registrar gastos diários/sazonais ou receitas (pensado para uso rápido no celular).
- Gastos Fixos: Interface para gerenciar/visualizar as contas fixas do mês (Condomínio, IPTU, Luz, etc.).
- Tela moderna, simples e fácil de usar, pensada na clareza, usabilidade e visibilidade 

## 4. Tarefa:
- Escreva o código completo e funcional para os seguintes arquivos:
- requirements.txt (todas as dependências necessárias).
- migrar.py (script executável para importar o Excel no banco).
- app.py (aplicação Streamlit modularizada, responsiva para celular e conectada ao Supabase via st.connection ou SQLAlchemy).
- .env.example (com a variável DATABASE_URL).
- Forneça o código limpo, simples, comentado e pronto para executar.
- Divida em etapas, adicione testes as etapas, e garanta que cada etapa seja testada e esteja funcionando antes de ir para próxima.
# SOSO — Sistema Operacional que Salva o Orçamento

Aplicação pessoal de controle financeiro para registrar receitas, despesas e investimentos, acompanhar o resultado mensal e centralizar contas fixas. A interface foi construída para ser simples e confortável tanto no computador quanto no celular.

## Funcionalidades

- Dashboard mensal com total ganho, total gasto, total investido e saldo.
- Gráfico comparativo da evolução mensal de receitas, despesas e investimentos.
- Cadastro rápido de lançamentos manuais.
- Cadastro e consulta de gastos fixos, como aluguel, condomínio, IPTU, luz e internet.
- Importação idempotente do histórico da planilha `financas.xlsx`: uma segunda execução não duplica lançamentos já importados.
- Persistência em PostgreSQL, incluindo projetos hospedados no Supabase.

## Tecnologias

- Python 3.10 ou superior
- Streamlit
- PostgreSQL / Supabase
- SQLAlchemy e `psycopg2-binary`
- Pandas e OpenPyXL
- Plotly
- Pytest

## Estrutura do projeto

```text
.
├── app.py               # Interface Streamlit
├── database.py          # Modelos SQLAlchemy e conexão com o banco
├── migrar.py            # Importação da planilha Excel
├── financas.xlsx        # Histórico financeiro de origem
├── requirements.txt     # Dependências Python
├── .env.example         # Modelo das variáveis de ambiente
└── tests/               # Testes automatizados
```

## Pré-requisitos

1. Python 3.10 ou mais recente instalado.
2. Um banco PostgreSQL acessível. Um projeto no [Supabase](https://supabase.com/) é uma opção prática.
3. A URL de conexão do banco. No Supabase, ela pode ser obtida em **Settings → Database → Connection string**.

## Instalação e configuração

Clone ou baixe o projeto e, no diretório dele, crie um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Crie o arquivo de configuração local a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` e informe a URL do seu banco:

```env
DATABASE_URL=postgresql+psycopg2://postgres:SUA_SENHA@db.SEUPROJETO.supabase.co:5432/postgres
```

> Nunca envie o arquivo `.env` ao repositório: ele contém uma credencial de acesso ao banco.

## Importar o histórico financeiro

Com a variável `DATABASE_URL` configurada, execute:

```powershell
python migrar.py --arquivo financas.xlsx
```

O script cria as tabelas necessárias e lê as abas anuais da planilha. Ele identifica receitas, despesas e investimentos; linhas de totais, como `Contas`, `Pessoal` e `Total`, são descartadas para evitar somas duplicadas. As despesas também criam registros de gastos fixos quando ainda não existem.

Para importar outro arquivo, informe seu caminho no parâmetro `--arquivo`.

## Executar a aplicação

```powershell
streamlit run app.py
```

O Streamlit exibirá o endereço local — normalmente `http://localhost:8501` — para abrir no navegador. Em um celular conectado à mesma rede, use o endereço de rede exibido pelo Streamlit.

## Login com Google e deploy no Streamlit Community Cloud

O SOSO bloqueia o acesso até que o visitante entre com Google e o e-mail seja
igual ao configurado em `access.allowed_email`. A aplicação falha fechada: sem
essa configuração, o orçamento não é exibido.

1. No Google Cloud Console, crie um cliente OAuth 2.0 do tipo **Web application**.
2. Adicione a URL de redirecionamento do Streamlit: `https://SEU-SUBDOMINIO.streamlit.app/oauth2callback`.
3. Copie `.streamlit/secrets.example.toml` para `.streamlit/secrets.toml` localmente e preencha `DATABASE_URL`, o e-mail autorizado, `cookie_secret`, `client_id` e `client_secret`.
4. No Streamlit Community Cloud, conecte sua conta GitHub, escolha o repositório e o arquivo `app.py`.
5. Em **Advanced settings → Secrets**, cole o conteúdo preenchido de `secrets.toml`. Nunca envie esse arquivo ao GitHub.

O arquivo `.streamlit/secrets.toml` já é ignorado pelo Git. O deploy atualiza automaticamente a cada envio de código ao repositório.

Na primeira inicialização, a aplicação cria automaticamente estas tabelas:

| Tabela | Finalidade |
| --- | --- |
| `categorias` | Organiza receitas, despesas e investimentos. |
| `gastos_fixos` | Armazena contas recorrentes e seus vencimentos. |
| `lancamentos` | Registra cada movimentação financeira. |

## Telas

### Dashboard

Exibe os indicadores do mês selecionado e um gráfico de comparação histórica de ganhos, gastos e investimentos.

### Novo lançamento

Permite salvar rapidamente uma receita, despesa ou investimento. Se a categoria ainda não existir, ela é criada automaticamente a partir da descrição informada.

### Gastos fixos

Lista as contas recorrentes importadas ou cadastradas manualmente e permite adicionar novas contas com valor previsto e dia de vencimento.

## Testes

Execute a suíte automatizada com:

```powershell
python -m pytest -q
```

Os testes usam SQLite temporário; portanto, não alteram nem exigem acesso ao Supabase. Eles verificam a criação das tabelas, a leitura de valores brasileiros como `R$ 2.504,08` e a idempotência da importação.

## Solução de problemas

- **`Defina DATABASE_URL`**: crie o `.env` a partir de `.env.example` e preencha a URL corretamente.
- **Erro ao conectar ao Supabase**: confira senha, host, porta, regras de rede e se a URL usa o prefixo `postgresql+psycopg2://`.
- **Planilha não encontrada**: informe o caminho correto, por exemplo `python migrar.py --arquivo C:\caminho\financas.xlsx`.
- **Dependências ausentes**: ative o ambiente virtual e execute novamente `python -m pip install -r requirements.txt`.

## Licença

Este projeto é distribuído sob a licença presente no arquivo [LICENSE](LICENSE).

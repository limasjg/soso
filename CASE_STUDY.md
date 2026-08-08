# Case study — SOSO

> Sistema Operacional para Salvar seu Orçamento

## Contexto

O SOSO é uma aplicação pessoal de controle financeiro criada para praticar
Python em um problema real: substituir a consulta e a atualização manual de uma
planilha financeira por uma experiência web mais organizada, visual e segura.

O projeto transforma dados históricos de uma planilha Excel em uma aplicação
capaz de acompanhar receitas, despesas, investimentos e planejamento mensal.

## Problema

Uma planilha é flexível, mas tende a dificultar a consulta do histórico, a
visualização de indicadores e a manutenção das contas de cada mês. O objetivo
foi centralizar essas informações em uma interface simples, acessível pelo
computador e celular, sem perder a persistência e o histórico dos dados.

## Solução

A solução foi construída como uma aplicação Streamlit conectada a um banco
PostgreSQL no Supabase. O histórico inicial é importado da planilha Excel e os
dados passam a ser manipulados pela aplicação.

```text
Usuário
  └─ Google OIDC
       └─ Streamlit Community Cloud
            └─ SQLAlchemy + psycopg2
                 └─ PostgreSQL no Supabase

GitHub ── push na branch develop ──> deploy automático no Streamlit
```

## Principais funcionalidades

- Dashboard mensal com receita, despesas, investimentos e saldo.
- Gráfico anual para comparar a evolução das movimentações.
- Planilha mensal de despesas com status `Pago` ou `Pendente`.
- Criação automática do planejamento de um mês a partir do mês anterior.
- Edição direta das tabelas e salvamento automático.
- Persistência de categorias, lançamentos, gastos planejados e gastos fixos.
- Importação idempotente do histórico em Excel, evitando duplicação de dados.
- Login via Google, restrito ao e-mail autorizado.
- Interface com tema escuro e contraste ajustado para desktop e celular.

## Tecnologias e decisões

| Tecnologia | Papel no projeto |
| --- | --- |
| Python | Linguagem principal da aplicação. |
| Streamlit | Interface web, componentes interativos e hospedagem no Community Cloud. |
| Pandas e OpenPyXL | Leitura, limpeza e transformação da planilha financeira. |
| SQLAlchemy | Modelagem das entidades e acesso ao banco de dados. |
| PostgreSQL / Supabase | Persistência dos dados financeiros em banco relacional gerenciado. |
| Plotly | Visualização gráfica da evolução financeira. |
| Authlib + Google OIDC | Autenticação do usuário sem expor o orçamento em uma URL pública. |
| Pytest | Testes da camada de banco e da importação. |

## Desafios técnicos e aprendizados

O principal desafio foi levar uma aplicação local para a nuvem sem expor
credenciais nem perder os dados. As configurações sensíveis — URL do banco,
segredos do OAuth e e-mail autorizado — foram mantidas fora do repositório e
configuradas pelo gerenciador de secrets do Streamlit.

No deploy, a conexão direta do Supabase não funcionou no ambiente hospedado
por depender de IPv6. A solução foi utilizar o Session Pooler do Supabase, que
permite a conexão IPv4 ao mesmo banco PostgreSQL. Assim, a aplicação local e a
publicada continuam lendo e alterando os mesmos dados.

Outro ponto foi a autenticação: o endereço de retorno do Google precisou ser
configurado com a URL final do Streamlit (`/oauth2callback`) tanto no Google
Cloud quanto nos secrets da aplicação.

## Resultado

O resultado é uma aplicação web publicada, com dados persistentes, acesso
restrito por login e fluxo de atualização contínua via GitHub. O projeto uniu
prática de Python, modelagem relacional, tratamento de dados, visualização,
autenticação e deploy em um produto funcional para uso pessoal.

## Próximos passos

- Expor no menu as telas de novo lançamento e detalhamento mensal, que já têm
  lógica implementada.
- Criar uma interface completa para gastos fixos.
- Adicionar exportação de dados e relatórios por período.
- Ampliar os testes para cobrir fluxos da interface e regras financeiras.
- Avaliar observabilidade, backups e recursos pagos caso o projeto cresça.

# 🛒 SistemaLoja PDV

Sistema desktop de **Ponto de Venda (PDV)** desenvolvido em **Python** e integrado ao **Microsoft SQL Server**, responsável pelo registro das operações de uma loja, incluindo vendas, produtos, estoque e movimentações de caixa.

O sistema faz parte do ecossistema **SistemaLoja** e está integrado a um **Dashboard Web**, que utiliza os dados registrados pelo PDV para gerar indicadores e análises das operações.

O projeto foi desenvolvido para estudo e portfólio, reunindo conceitos de desenvolvimento de sistemas, banco de dados, APIs e análise de dados.

---

## 🖥️ Interface do sistema

### Tela principal

Tela inicial do SistemaLoja, com acesso às principais funcionalidades do PDV.

![Tela principal do PDV](docs/images/pdv-principal.png)

---

### 🛒 Registro de venda

Tela utilizada para adicionar produtos ao carrinho, controlar quantidades e acompanhar o valor total da compra.

![Tela de venda](docs/images/venda.png)

---

### 💳 Forma de pagamento

Durante a finalização da venda, o sistema permite selecionar diferentes formas de pagamento.

![Formas de pagamento](docs/images/forma-de-pagamento.png)

---

### 💵 Pagamento em dinheiro

Para pagamentos em dinheiro, o sistema permite informar o valor recebido e realiza automaticamente o cálculo do troco.

![Pagamento em dinheiro](docs/images/dinheiro.png)

---

### 📦 Produtos e estoque

Área destinada ao cadastro, consulta e gerenciamento dos produtos disponíveis na loja.

![Controle de estoque](docs/images/estoque.png)

---

## ✨ Funcionalidades

O SistemaLoja PDV possui recursos como:

- Cadastro e edição de produtos
- Controle de estoque
- Consulta de preços por código de barras
- Registro de vendas
- Carrinho de compras
- Controle de quantidade dos produtos
- Abertura de caixa
- Fechamento de caixa
- Controle de fundo de caixa
- Pagamento em dinheiro
- Pagamento via PIX
- Pagamento no débito
- Pagamento no crédito
- Cálculo automático de troco
- Histórico de vendas
- Consulta de detalhes das vendas
- Cancelamento de vendas
- Retorno automático dos produtos ao estoque após cancelamento
- Relatórios de vendas
- Ranking de produtos vendidos
- Integração com dashboard de análise de dados

---

## 🛠️ Tecnologias utilizadas

### Desenvolvimento

- Python
- Tkinter
- ttk
- PyODBC

### Banco de dados

- Microsoft SQL Server
- SQL
- SQLite

### Integração e análise

- Python
- Flask
- API REST
- Google Apps Script
- JavaScript
- Chart.js

### Versionamento

- Git
- GitHub

---

## 🗃️ Banco de dados

O sistema utiliza o banco de dados:

```text
SistemaLoja
```

As principais tabelas utilizadas são:

```text
produtos
caixas
vendas
itens_venda
```

O arquivo:

```text
schema.sql
```

contém a estrutura utilizada para criação das tabelas do banco.

---

## 🏗️ Arquitetura do SistemaLoja

O PDV é responsável pela geração e registro dos dados operacionais.

Esses dados são armazenados no Microsoft SQL Server e posteriormente consumidos pelo Dashboard Web por meio de uma API desenvolvida em Python e Flask.

```text
             SISTEMALOJA

┌─────────────────────────────┐
│        Sistema PDV          │
│      Python + Tkinter       │
│                             │
│  Vendas • Caixa • Estoque   │
│         Produtos            │
└──────────────┬──────────────┘
               │
               │ SQL / PyODBC
               ▼
┌─────────────────────────────┐
│    Microsoft SQL Server     │
│                             │
│        SistemaLoja          │
│                             │
│ produtos                    │
│ caixas                      │
│ vendas                      │
│ itens_venda                 │
└──────────────┬──────────────┘
               │
               │ Consultas SQL
               ▼
┌─────────────────────────────┐
│     API Python / Flask      │
│                             │
│  Disponibilização dos dados │
└──────────────┬──────────────┘
               │
               │ JSON / HTTP
               ▼
┌─────────────────────────────┐
│       Dashboard Web         │
│                             │
│ Google Apps Script          │
│ JavaScript                  │
│ Chart.js                    │
└─────────────────────────────┘
```

Mais informações sobre a arquitetura do projeto estão disponíveis em:

```text
architecture.md
```

---

## 📊 Integração com Dashboard Web

O SistemaLoja PDV está integrado a um dashboard desenvolvido especificamente para análise dos dados gerados pelas operações da loja.

Quando uma venda é realizada no PDV, as informações são registradas no **Microsoft SQL Server**.

Uma API desenvolvida em **Python e Flask** consulta o banco e disponibiliza essas informações para o Dashboard Web.

O dashboard permite acompanhar indicadores como:

- Faturamento
- Quantidade de vendas
- Ticket médio
- Formas de pagamento
- Produtos mais vendidos
- Estoque baixo
- Evolução das vendas por período

Também foram implementados filtros interativos que permitem cruzar informações por produto, período e forma de pagamento.

---

## 🔗 SistemaLoja Dashboard

O Dashboard Web possui um repositório próprio no GitHub.

### 📊 SistemaLoja Dashboard

[Ver o SistemaLoja Dashboard no GitHub](https://github.com/gabrielnasc17/sistemaloja-dashboard)

O projeto do dashboard contém a API responsável pela comunicação com o banco de dados e a interface web utilizada para visualização dos indicadores.

Dessa forma, os dois projetos trabalham de maneira integrada:

```text
SistemaLoja PDV
       +
SistemaLoja Dashboard
       =
Sistema completo de operação e análise
```

---

## 📂 Estrutura do projeto

```text
sistemaloja-pdv/
│
├── sistema_loja.py
├── migrar_sqlserver.py
├── schema.sql
├── architecture.md
├── requirements.txt
├── README.md
├── LICENSE
│
└── docs/
    └── images/
        ├── pdv-principal.png
        ├── venda.png
        ├── forma-de-pagamento.png
        ├── dinheiro.png
        └── estoque.png
```

---

## 🔄 Migração SQLite → SQL Server

Durante a evolução do projeto, o sistema passou de uma estrutura utilizando **SQLite** para **Microsoft SQL Server**.

Para realizar essa migração foi desenvolvido o script:

```text
migrar_sqlserver.py
```

O script realiza a transferência dos dados preservando os relacionamentos entre:

```text
Produtos
   │
   ▼
Itens da venda
   │
   ▼
Vendas
   │
   ▼
Caixas
```

Também são realizadas verificações antes da migração para evitar a duplicação de dados no banco de destino.

---

## ⚙️ Requisitos

Para executar o projeto é necessário possuir:

```text
Python 3
Microsoft SQL Server
ODBC Driver 18 for SQL Server
```

Instale as dependências utilizando:

```bash
pip install -r requirements.txt
```

---

## ▶️ Executando o projeto

Com o SQL Server instalado e o banco configurado:

```bash
python sistema_loja.py
```

A configuração padrão do projeto utiliza:

```text
Servidor: localhost
Banco: SistemaLoja
Autenticação: Windows
```

Esses valores podem ser configurados através das variáveis de ambiente:

```text
SISTEMALOJA_SQL_SERVER
SISTEMALOJA_SQL_DATABASE
```

---

## 🔐 Segurança

O repositório público não contém:

- Senhas
- Tokens de acesso
- Credenciais do SQL Server
- Dados reais de clientes
- Banco de dados local
- Arquivos de build da aplicação

A conexão com o SQL Server utiliza autenticação do Windows na configuração padrão.

---

## 🤖 Uso de Inteligência Artificial

Durante o desenvolvimento utilizei **Inteligência Artificial como ferramenta de apoio**.

A IA foi utilizada principalmente em atividades como:

- Revisão de código
- Identificação e correção de erros
- Debugging
- Sugestões de melhorias
- Organização da estrutura do projeto
- Melhorias de interface
- Análise de segurança
- Documentação
- Implementação e evolução de funcionalidades

As regras de negócio, funcionamento do sistema, testes e decisões sobre a aplicação foram avaliadas e ajustadas durante o desenvolvimento do projeto.

---

## 🚀 Possíveis evoluções

Algumas melhorias que podem ser adicionadas futuramente:

- Controle de usuários e permissões no PDV
- Auditoria de operações
- Exportação de relatórios
- Backup automatizado do banco
- Instalador da aplicação
- Novos relatórios operacionais
- Mais indicadores no Dashboard
- Controle de múltiplas lojas
- Controle de múltiplos caixas

---

## 🎯 Objetivo do projeto

O SistemaLoja foi desenvolvido como projeto de estudo e portfólio com o objetivo de aplicar conhecimentos de:

```text
Desenvolvimento de sistemas
        +
Banco de dados
        +
SQL
        +
APIs
        +
Análise de dados
        +
Dashboards
```

O projeto permite acompanhar todo o fluxo, desde a geração do dado durante uma venda até sua utilização para análise e tomada de decisão.

---

## 👨‍💻 Autor

**Gabriel Nascimento**

Projeto desenvolvido para estudo e portfólio com foco em **Python, SQL Server, Banco de Dados, APIs, BI e Análise de Dados**.

### Projetos relacionados

🛒 **SistemaLoja PDV**  
Sistema responsável pelas operações de venda, estoque e caixa.

📊 **SistemaLoja Dashboard**  
https://github.com/gabrielnasc17/sistemaloja-dashboard

# 🛒 SistemaLoja PDV

Sistema desktop de **ponto de venda (PDV)** desenvolvido em Python com integração ao **Microsoft SQL Server**.

O projeto foi criado para centralizar rotinas de venda, controle de estoque, abertura e fechamento de caixa, consulta de preços, histórico e relatórios operacionais.

> Projeto desenvolvido para estudo e portfólio, com apoio de IA em etapas de revisão, depuração, melhoria de interface e evolução do código.

---

## 🖥️ Visão geral

![SistemaLoja PDV](docs/images/dashboard.png)

> Adicione um print do sistema em `docs/images/dashboard.png`.

---

## ✨ Funcionalidades

- Cadastro e edição de produtos
- Controle de estoque
- Consulta de preço por código de barras
- Abertura e fechamento de caixa
- Registro de vendas
- Leitura/entrada de código de barras
- Pagamento em dinheiro, PIX, débito e crédito
- Cálculo de troco
- Histórico de vendas
- Detalhes dos itens vendidos
- Cancelamento de venda com retorno dos itens ao estoque
- Relatório diário
- Ranking de produtos vendidos
- Migração de dados de SQLite para SQL Server

---

## 🧱 Tecnologias

- Python
- Tkinter / ttk
- Microsoft SQL Server
- SQL
- PyODBC
- SQLite (utilizado no processo de migração)
- Git
- GitHub

---

## 🗃️ Banco de dados

O banco `SistemaLoja` utiliza as tabelas principais:

- `produtos`
- `caixas`
- `vendas`
- `itens_venda`

A estrutura SQL de referência está disponível em:

```text
database/schema.sql
```

---

## 🏗️ Arquitetura

```text
Usuário / Operador
       │
       ▼
Python + Tkinter
       │
       │ PyODBC
       ▼
Microsoft SQL Server
       │
       ├── Produtos / Estoque
       ├── Caixas
       ├── Vendas
       └── Itens das vendas
```

Mais detalhes em [`docs/architecture.md`](docs/architecture.md).

---

## 📂 Estrutura

```text
sistemaloja-pdv/
│
├── src/
│   ├── sistema_loja.py
│   └── migrar_sqlserver.py
│
├── database/
│   └── schema.sql
│
├── docs/
│   ├── architecture.md
│   └── images/
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## ⚙️ Pré-requisitos

- Python 3
- Microsoft SQL Server
- ODBC Driver 18 for SQL Server
- Banco `SistemaLoja`

Instale a dependência Python:

```bash
pip install -r requirements.txt
```

Por padrão, a aplicação utiliza:

```text
Servidor: localhost
Banco: SistemaLoja
Autenticação: Windows / Trusted Connection
```

Você também pode alterar servidor e banco por variáveis de ambiente:

### Windows CMD

```bat
set SISTEMALOJA_SQL_SERVER=localhost
set SISTEMALOJA_SQL_DATABASE=SistemaLoja
py src\sistema_loja.py
```

---

## ▶️ Executando

```bash
python src/sistema_loja.py
```

A aplicação cria/verifica as tabelas necessárias no banco ao iniciar.

---

## 🔄 Migração SQLite → SQL Server

O arquivo:

```text
src/migrar_sqlserver.py
```

foi criado para migrar um banco legado `loja.db` para o SQL Server preservando os IDs e relacionamentos entre produtos, caixas, vendas e itens.

O script verifica o banco de destino antes da migração e não prossegue caso encontre dados nas tabelas de destino.

---

## 🔒 Segurança do repositório

O projeto público não inclui:

- banco `loja.db`
- dados reais de vendas
- senhas
- tokens
- credenciais SQL
- arquivos de build

A conexão padrão utiliza `Trusted_Connection=yes`, sem senha hardcoded.

---

## 🤖 Uso de IA no desenvolvimento

IA foi utilizada como ferramenta de apoio durante o projeto para:

- revisão de código
- identificação e correção de erros
- sugestões de interface
- análise de pontos fracos
- refatoração e documentação

As decisões sobre regras do sistema, fluxo do PDV, banco de dados e validação das funcionalidades fizeram parte do desenvolvimento do projeto.

---

## 🚀 Próximas evoluções

- Integração direta com o dashboard web do SistemaLoja
- Perfis de usuário e permissões
- Auditoria de operações
- Exportação de relatórios
- Instalador/empacotamento da aplicação

---

## 👨‍💻 Autor

**Gabriel Nascimento**

Projeto de portfólio com foco em desenvolvimento de sistemas, banco de dados e análise de dados.

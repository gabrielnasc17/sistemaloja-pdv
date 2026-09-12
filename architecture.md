# Arquitetura

```text
Operador
   │
   ▼
Aplicação desktop
Python + Tkinter
   │
   │ pyodbc
   ▼
Microsoft SQL Server
SistemaLoja
   │
   ├── produtos
   ├── caixas
   ├── vendas
   └── itens_venda
```

O sistema concentra as operações de PDV, estoque, caixa e relatórios em uma aplicação desktop.
As operações críticas de venda e cancelamento utilizam transações no SQL Server para preservar a consistência dos dados.

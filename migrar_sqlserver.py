import os
import sqlite3
import pyodbc
from decimal import Decimal, ROUND_HALF_UP


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

ARQUIVO_SQLITE = "loja.db"

SQL_SERVER = os.getenv("SISTEMALOJA_SQL_SERVER", "localhost")
SQL_DATABASE = os.getenv("SISTEMALOJA_SQL_DATABASE", "SistemaLoja")

CONEXAO_SQL_SERVER = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


# ==========================================================
# FUNÇÕES
# ==========================================================

def dinheiro(valor):
    if valor is None:
        return None

    return Decimal(str(valor)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def tabela_existe_sqlite(cursor, tabela):
    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (tabela,)
    )

    return cursor.fetchone() is not None


def quantidade_sqlite(cursor, tabela):
    cursor.execute(
        f"SELECT COUNT(*) FROM {tabela}"
    )

    return cursor.fetchone()[0]


def quantidade_sqlserver(cursor, tabela):
    cursor.execute(
        f"SELECT COUNT(*) FROM dbo.{tabela}"
    )

    return cursor.fetchone()[0]


# ==========================================================
# INÍCIO
# ==========================================================

print("=" * 60)
print("MIGRAÇÃO SQLITE -> SQL SERVER")
print("=" * 60)
print()


# ==========================================================
# VERIFICAR ARQUIVO SQLITE
# ==========================================================

if not os.path.exists(ARQUIVO_SQLITE):
    print("ERRO!")
    print()
    print(
        f"O arquivo {ARQUIVO_SQLITE} não foi encontrado."
    )
    print()
    print(
        "Execute este programa dentro da pasta do SistemaLoja."
    )
    input("\nPressione ENTER para sair...")
    raise SystemExit


# ==========================================================
# CONECTAR SQLITE
# ==========================================================

try:
    sqlite = sqlite3.connect(
        ARQUIVO_SQLITE
    )

    cursor_sqlite = sqlite.cursor()

    print("SQLite conectado.")

except Exception as erro:
    print()
    print("ERRO AO ABRIR O SQLITE:")
    print(erro)

    input("\nPressione ENTER para sair...")
    raise SystemExit


# ==========================================================
# CONECTAR SQL SERVER
# ==========================================================

try:
    sqlserver = pyodbc.connect(
        CONEXAO_SQL_SERVER,
        autocommit=False
    )

    cursor_sqlserver = sqlserver.cursor()

    print("SQL Server conectado.")

except Exception as erro:
    sqlite.close()

    print()
    print("ERRO AO CONECTAR NO SQL SERVER:")
    print(erro)

    input("\nPressione ENTER para sair...")
    raise SystemExit


# ==========================================================
# VERIFICAR TABELAS DO SQLITE
# ==========================================================

tabelas = [
    "produtos",
    "caixas",
    "vendas",
    "itens_venda"
]

print()
print("Verificando banco antigo...")

for tabela in tabelas:
    if not tabela_existe_sqlite(
        cursor_sqlite,
        tabela
    ):
        print()
        print(
            f"ERRO: tabela '{tabela}' não existe no loja.db."
        )

        sqlite.close()
        sqlserver.close()

        input("\nPressione ENTER para sair...")
        raise SystemExit

    quantidade = quantidade_sqlite(
        cursor_sqlite,
        tabela
    )

    print(
        f"{tabela}: {quantidade} registro(s)"
    )


# ==========================================================
# VERIFICAR SE SQL SERVER ESTÁ VAZIO
# ==========================================================

print()
print("Verificando banco novo...")

banco_novo_tem_dados = False

for tabela in tabelas:
    quantidade = quantidade_sqlserver(
        cursor_sqlserver,
        tabela
    )

    print(
        f"{tabela}: {quantidade} registro(s)"
    )

    if quantidade > 0:
        banco_novo_tem_dados = True


if banco_novo_tem_dados:
    print()
    print("=" * 60)
    print("MIGRAÇÃO CANCELADA")
    print("=" * 60)
    print()
    print(
        "O SQL Server já possui dados em uma ou mais tabelas."
    )
    print(
        "O programa não vai apagar nem duplicar esses dados."
    )
    print()
    print(
        "Revise o banco de destino antes de continuar."
    )

    sqlite.close()
    sqlserver.close()

    input("\nPressione ENTER para sair...")
    raise SystemExit


# ==========================================================
# CONFIRMAÇÃO
# ==========================================================

print()
print("=" * 60)
print("PRONTO PARA MIGRAR")
print("=" * 60)
print()
print(
    "Os IDs originais serão mantidos para preservar"
)
print(
    "os relacionamentos entre produtos, vendas e caixas."
)
print()

confirmacao = input(
    "Digite MIGRAR para continuar: "
).strip().upper()


if confirmacao != "MIGRAR":
    print()
    print("Migração cancelada.")

    sqlite.close()
    sqlserver.close()

    input("\nPressione ENTER para sair...")
    raise SystemExit


# ==========================================================
# MIGRAÇÃO
# ==========================================================

try:
    print()
    print("Iniciando migração...")
    print()


    # ======================================================
    # PRODUTOS
    # ======================================================

    print("Migrando produtos...")

    cursor_sqlite.execute("""
        SELECT
            id,
            codigo_barras,
            nome,
            categoria,
            preco,
            estoque
        FROM produtos
        ORDER BY id
    """)

    produtos = cursor_sqlite.fetchall()

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.produtos ON"
    )

    for produto in produtos:
        cursor_sqlserver.execute("""
            INSERT INTO dbo.produtos (
                id,
                codigo_barras,
                nome,
                categoria,
                preco,
                estoque
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            produto[0],
            produto[1],
            produto[2],
            produto[3],
            dinheiro(produto[4]),
            produto[5]
        ))

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.produtos OFF"
    )

    print(
        f"OK - {len(produtos)} produto(s)"
    )


    # ======================================================
    # CAIXAS
    # ======================================================

    print("Migrando caixas...")

    cursor_sqlite.execute("""
        SELECT
            id,
            data_abertura,
            valor_inicial,
            data_fechamento,
            valor_contado,
            valor_esperado,
            diferenca,
            status
        FROM caixas
        ORDER BY id
    """)

    caixas = cursor_sqlite.fetchall()

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.caixas ON"
    )

    for caixa in caixas:
        cursor_sqlserver.execute("""
            INSERT INTO dbo.caixas (
                id,
                data_abertura,
                valor_inicial,
                data_fechamento,
                valor_contado,
                valor_esperado,
                diferenca,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            caixa[0],
            caixa[1],
            dinheiro(caixa[2]),
            caixa[3],
            dinheiro(caixa[4]),
            dinheiro(caixa[5]),
            dinheiro(caixa[6]),
            caixa[7]
        ))

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.caixas OFF"
    )

    print(
        f"OK - {len(caixas)} caixa(s)"
    )


    # ======================================================
    # VENDAS
    # ======================================================

    print("Migrando vendas...")

    cursor_sqlite.execute("""
        SELECT
            id,
            data,
            valor_total,
            forma_pagamento,
            valor_recebido,
            troco,
            caixa_id
        FROM vendas
        ORDER BY id
    """)

    vendas = cursor_sqlite.fetchall()

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.vendas ON"
    )

    for venda in vendas:
        cursor_sqlserver.execute("""
            INSERT INTO dbo.vendas (
                id,
                data,
                valor_total,
                forma_pagamento,
                valor_recebido,
                troco,
                caixa_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            venda[0],
            venda[1],
            dinheiro(venda[2]),
            venda[3],
            dinheiro(venda[4]),
            dinheiro(venda[5]) or Decimal("0.00"),
            venda[6]
        ))

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.vendas OFF"
    )

    print(
        f"OK - {len(vendas)} venda(s)"
    )


    # ======================================================
    # ITENS DA VENDA
    # ======================================================

    print("Migrando itens das vendas...")

    cursor_sqlite.execute("""
        SELECT
            id,
            venda_id,
            produto_id,
            quantidade,
            preco_unitario,
            subtotal
        FROM itens_venda
        ORDER BY id
    """)

    itens = cursor_sqlite.fetchall()

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.itens_venda ON"
    )

    for item in itens:
        cursor_sqlserver.execute("""
            INSERT INTO dbo.itens_venda (
                id,
                venda_id,
                produto_id,
                quantidade,
                preco_unitario,
                subtotal
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item[0],
            item[1],
            item[2],
            item[3],
            dinheiro(item[4]),
            dinheiro(item[5])
        ))

    cursor_sqlserver.execute(
        "SET IDENTITY_INSERT dbo.itens_venda OFF"
    )

    print(
        f"OK - {len(itens)} item(ns)"
    )


    # ======================================================
    # CONFIRMAR TRANSAÇÃO
    # ======================================================

    sqlserver.commit()

    print()
    print("=" * 60)
    print("DADOS COPIADOS!")
    print("=" * 60)


except Exception as erro:
    sqlserver.rollback()

    print()
    print("=" * 60)
    print("ERRO NA MIGRAÇÃO")
    print("=" * 60)
    print()
    print(erro)
    print()
    print(
        "Nenhuma alteração dessa migração foi confirmada."
    )

    sqlite.close()
    sqlserver.close()

    input("\nPressione ENTER para sair...")
    raise SystemExit


# ==========================================================
# CONFERÊNCIA
# ==========================================================

print()
print("Conferindo quantidades...")
print()

tudo_certo = True

for tabela in tabelas:
    origem = quantidade_sqlite(
        cursor_sqlite,
        tabela
    )

    destino = quantidade_sqlserver(
        cursor_sqlserver,
        tabela
    )

    if origem == destino:
        status = "OK"

    else:
        status = "DIFERENTE"
        tudo_certo = False

    print(
        f"{tabela:<15} "
        f"SQLite: {origem:<5} "
        f"SQL Server: {destino:<5} "
        f"{status}"
    )


# ==========================================================
# FECHAR CONEXÕES
# ==========================================================

sqlite.close()
sqlserver.close()


# ==========================================================
# RESULTADO
# ==========================================================

print()

if tudo_certo:
    print("=" * 60)
    print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print(
        "Os dados do loja.db agora também estão no SQL Server."
    )
    print()
    print(
        "NÃO apague o loja.db ainda."
    )

else:
    print("=" * 60)
    print("ATENÇÃO")
    print("=" * 60)
    print()
    print(
        "As quantidades não ficaram iguais."
    )
    print(
        "Não altere o sistema ainda."
    )


input("\nPressione ENTER para sair...")
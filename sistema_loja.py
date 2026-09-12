import os
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from difflib import SequenceMatcher
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone, timedelta


# ==========================================================
# TEMA VISUAL
# ==========================================================
# Mantém o Tkinter puro: não precisa instalar biblioteca extra.
COR_FUNDO = "#F3F6FA"
COR_CARD = "#FFFFFF"
COR_CABECALHO = "#0F172A"
COR_PRIMARIA = "#2563EB"
COR_PRIMARIA_HOVER = "#1D4ED8"
COR_TEXTO = "#172033"
COR_TEXTO_SECUNDARIO = "#667085"
COR_BORDA = "#D9E1EA"
COR_SUCESSO = "#15803D"
COR_SUCESSO_CLARO = "#DCFCE7"
COR_ALERTA = "#B45309"
COR_ALERTA_CLARO = "#FEF3C7"
COR_PERIGO = "#B42318"
COR_PERIGO_HOVER = "#912018"
COR_PERIGO_CLARO = "#FEE4E2"
FONTE = "Segoe UI"


def configurar_tema(root):
    """Aplica uma identidade visual única a toda a aplicação."""
    root.configure(bg=COR_FUNDO)

    # Widgets Tk clássicos usados nas telas antigas.
    root.option_add("*Font", (FONTE, 10))
    root.option_add("*Frame.background", COR_FUNDO)
    root.option_add("*Label.background", COR_FUNDO)
    root.option_add("*Label.foreground", COR_TEXTO)
    root.option_add("*Canvas.background", COR_FUNDO)

    root.option_add("*Entry.background", "#FFFFFF")
    root.option_add("*Entry.foreground", COR_TEXTO)
    root.option_add("*Entry.insertBackground", COR_TEXTO)
    root.option_add("*Entry.relief", "flat")
    root.option_add("*Entry.highlightThickness", 1)
    root.option_add("*Entry.highlightBackground", COR_BORDA)
    root.option_add("*Entry.highlightColor", COR_PRIMARIA)

    root.option_add("*Button.background", COR_PRIMARIA)
    root.option_add("*Button.foreground", "#FFFFFF")
    root.option_add("*Button.activeBackground", COR_PRIMARIA_HOVER)
    root.option_add("*Button.activeForeground", "#FFFFFF")
    root.option_add("*Button.relief", "flat")
    root.option_add("*Button.borderWidth", 0)
    root.option_add("*Button.cursor", "hand2")
    root.option_add("*Button.padX", 12)
    root.option_add("*Button.padY", 8)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Treeview",
        background="#FFFFFF",
        fieldbackground="#FFFFFF",
        foreground=COR_TEXTO,
        rowheight=34,
        borderwidth=0,
        font=(FONTE, 10)
    )
    style.configure(
        "Treeview.Heading",
        background="#E8EEF7",
        foreground=COR_TEXTO,
        relief="flat",
        borderwidth=0,
        padding=(10, 9),
        font=(FONTE, 10, "bold")
    )
    style.map(
        "Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", COR_TEXTO)]
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#DCE6F4")]
    )

    style.configure(
        "Vertical.TScrollbar",
        background="#CBD5E1",
        troughcolor=COR_FUNDO,
        bordercolor=COR_FUNDO,
        arrowcolor=COR_TEXTO_SECUNDARIO
    )
    style.configure(
        "Horizontal.TScrollbar",
        background="#CBD5E1",
        troughcolor=COR_FUNDO,
        bordercolor=COR_FUNDO,
        arrowcolor=COR_TEXTO_SECUNDARIO
    )


def botao_moderno(parent, texto, comando, cor=COR_PRIMARIA,
                   cor_ativa=None, fonte=(FONTE, 11, "bold"),
                   padx=18, pady=12, anchor="center"):
    if cor_ativa is None:
        cor_ativa = COR_PRIMARIA_HOVER if cor == COR_PRIMARIA else cor

    return tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=cor,
        fg="#FFFFFF",
        activebackground=cor_ativa,
        activeforeground="#FFFFFF",
        font=fonte,
        relief="flat",
        bd=0,
        highlightthickness=0,
        cursor="hand2",
        padx=padx,
        pady=pady,
        anchor=anchor
    )


def criar_card(parent, bg=COR_CARD, padx=20, pady=18):
    return tk.Frame(
        parent,
        bg=bg,
        bd=0,
        highlightthickness=1,
        highlightbackground=COR_BORDA,
        padx=padx,
        pady=pady
    )


# ==========================================================
# CONFIGURAÇÃO DO SQL SERVER
# ==========================================================

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
# BANCO DE DADOS
# ==========================================================

def conectar():
    return pyodbc.connect(
        CONEXAO_SQL_SERVER,
        timeout=5,
        autocommit=False
    )


def preparar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            IF OBJECT_ID('dbo.produtos', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.produtos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    codigo_barras NVARCHAR(50) NOT NULL UNIQUE,
                    nome NVARCHAR(200) NOT NULL,
                    categoria NVARCHAR(100),
                    preco DECIMAL(12,2) NOT NULL,
                    estoque INT NOT NULL DEFAULT 0
                );
            END
        """)

        cursor.execute("""
            IF OBJECT_ID('dbo.caixas', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.caixas (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    data_abertura DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
                    valor_inicial DECIMAL(12,2) NOT NULL,
                    data_fechamento DATETIME2(0),
                    valor_contado DECIMAL(12,2),
                    valor_esperado DECIMAL(12,2),
                    diferenca DECIMAL(12,2),
                    status NVARCHAR(20) NOT NULL DEFAULT 'ABERTO'
                );
            END
        """)

        cursor.execute("""
            IF OBJECT_ID('dbo.vendas', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.vendas (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    data DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
                    valor_total DECIMAL(12,2) NOT NULL,
                    forma_pagamento NVARCHAR(30) NOT NULL,
                    valor_recebido DECIMAL(12,2),
                    troco DECIMAL(12,2) NOT NULL DEFAULT 0,
                    caixa_id INT,
                    status NVARCHAR(20) DEFAULT 'CONCLUIDA',
                    data_cancelamento DATETIME2(0),
                    motivo_cancelamento NVARCHAR(500),
                    CONSTRAINT FK_vendas_caixas
                        FOREIGN KEY (caixa_id) REFERENCES dbo.caixas(id)
                );
            END
        """)

        cursor.execute("""
            IF OBJECT_ID('dbo.itens_venda', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.itens_venda (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    venda_id INT NOT NULL,
                    produto_id INT NOT NULL,
                    quantidade INT NOT NULL,
                    preco_unitario DECIMAL(12,2) NOT NULL,
                    subtotal DECIMAL(12,2) NOT NULL,
                    CONSTRAINT FK_itens_venda_vendas
                        FOREIGN KEY (venda_id) REFERENCES dbo.vendas(id),
                    CONSTRAINT FK_itens_venda_produtos
                        FOREIGN KEY (produto_id) REFERENCES dbo.produtos(id)
                );
            END
        """)

        # Atualiza bancos que já existiam antes do cancelamento de venda.
        cursor.execute("""
            IF COL_LENGTH('dbo.vendas', 'status') IS NULL
                ALTER TABLE dbo.vendas ADD status NVARCHAR(20) NULL;
        """)

        cursor.execute("""
            IF COL_LENGTH('dbo.vendas', 'data_cancelamento') IS NULL
                ALTER TABLE dbo.vendas ADD data_cancelamento DATETIME2(0) NULL;
        """)

        cursor.execute("""
            IF COL_LENGTH('dbo.vendas', 'motivo_cancelamento') IS NULL
                ALTER TABLE dbo.vendas ADD motivo_cancelamento NVARCHAR(500) NULL;
        """)

        cursor.execute("""
            UPDATE dbo.vendas
            SET status = 'CONCLUIDA'
            WHERE status IS NULL OR LTRIM(RTRIM(status)) = '';
        """)

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def dinheiro(valor):
    if valor is None:
        return None

    return Decimal(str(valor)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def moeda(valor):
    if valor is None:
        return "-"

    valor = dinheiro(valor)

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def converter_valor(texto):
    texto = texto.strip().replace("R$", "").strip()

    if not texto:
        raise ValueError

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return dinheiro(Decimal(texto))


def texto_normalizado(texto):
    return str(texto).strip().lower()


def similaridade(a, b):
    return SequenceMatcher(
        None,
        texto_normalizado(a),
        texto_normalizado(b)
    ).ratio()


def formatar_data_local(valor):
    if valor is None:
        return "-"

    if isinstance(valor, str):
        try:
            valor = datetime.fromisoformat(valor)
        except ValueError:
            return valor

    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)

    return valor.astimezone().strftime("%d/%m/%Y %H:%M:%S")


def limites_hoje_utc():
    agora_local = datetime.now().astimezone()
    inicio_local = agora_local.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
    fim_local = inicio_local + timedelta(days=1)

    inicio_utc = inicio_local.astimezone(timezone.utc).replace(tzinfo=None)
    fim_utc = fim_local.astimezone(timezone.utc).replace(tzinfo=None)

    return inicio_utc, fim_utc


def limites_data_local_utc(data_local):
    """Recebe uma data local e devolve o início/fim desse dia em UTC, sem timezone."""
    if isinstance(data_local, str):
        data_local = datetime.strptime(data_local.strip(), "%d/%m/%Y")

    agora_tz = datetime.now().astimezone().tzinfo
    inicio_local = datetime(
        data_local.year,
        data_local.month,
        data_local.day,
        0, 0, 0,
        tzinfo=agora_tz
    )
    fim_local = inicio_local + timedelta(days=1)

    inicio_utc = inicio_local.astimezone(timezone.utc).replace(tzinfo=None)
    fim_utc = fim_local.astimezone(timezone.utc).replace(tzinfo=None)
    return inicio_utc, fim_utc


def formatar_data_filtro(data):
    return data.strftime("%d/%m/%Y")


# ==========================================================
# ÁREA ROLÁVEL
# ==========================================================

def criar_area_rolavel(container):
    externo = tk.Frame(container, bg=COR_FUNDO)
    externo.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        externo,
        highlightthickness=0,
        bg=COR_FUNDO,
        bd=0
    )

    barra_vertical = ttk.Scrollbar(
        externo,
        orient="vertical",
        command=canvas.yview
    )

    barra_horizontal = ttk.Scrollbar(
        externo,
        orient="horizontal",
        command=canvas.xview
    )

    canvas.configure(
        yscrollcommand=barra_vertical.set,
        xscrollcommand=barra_horizontal.set
    )

    barra_vertical.pack(side="right", fill="y")
    barra_horizontal.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    conteudo = tk.Frame(canvas, bg=COR_FUNDO)
    janela_canvas = canvas.create_window(
        (0, 0),
        window=conteudo,
        anchor="nw"
    )

    def atualizar_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    conteudo.bind("<Configure>", atualizar_scroll)

    def ajustar_largura(event):
        largura_conteudo = conteudo.winfo_reqwidth()

        if largura_conteudo <= event.width:
            canvas.itemconfigure(janela_canvas, width=event.width)
        else:
            canvas.itemconfigure(janela_canvas, width=largura_conteudo)

    canvas.bind("<Configure>", ajustar_largura)

    def rolar_mouse(event):
        if event.delta:
            passos = int(-1 * (event.delta / 120))
            if passos == 0:
                passos = -1 if event.delta > 0 else 1
            canvas.yview_scroll(passos, "units")
        return "break"

    def rolar_cima(event):
        canvas.yview_scroll(-1, "units")
        return "break"

    def rolar_baixo(event):
        canvas.yview_scroll(1, "units")
        return "break"

    def ativar_scroll(event=None):
        canvas.bind_all("<MouseWheel>", rolar_mouse)
        canvas.bind_all("<Button-4>", rolar_cima)
        canvas.bind_all("<Button-5>", rolar_baixo)

    def desativar_scroll(event=None):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    externo.bind("<Enter>", ativar_scroll)
    externo.bind("<Leave>", desativar_scroll)
    conteudo.bind("<Enter>", ativar_scroll)
    conteudo.bind("<Leave>", desativar_scroll)

    return conteudo

def criar_tela(titulo, largura=800, altura=600, parent=None):
    if parent is None:
        parent = janela

    tela = tk.Toplevel(parent)
    tela.title(titulo)
    tela.configure(bg=COR_FUNDO)

    largura_tela = tela.winfo_screenwidth()
    altura_tela = tela.winfo_screenheight()

    largura_final = min(largura, max(400, largura_tela - 80))
    altura_final = min(altura, max(350, altura_tela - 120))

    tela.geometry(f"{largura_final}x{altura_final}")
    tela.minsize(min(420, largura_final), min(360, altura_final))

    conteudo = criar_area_rolavel(tela)
    return tela, conteudo

# ==========================================================
# CAIXA
# ==========================================================

def buscar_caixa_aberto():
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT TOP 1
                id,
                data_abertura,
                valor_inicial
            FROM dbo.caixas
            WHERE status = 'ABERTO'
            ORDER BY id DESC
        """)
        return cursor.fetchone()

    finally:
        conexao.close()


def atualizar_status_caixa():
    try:
        caixa = buscar_caixa_aberto()

        if caixa:
            label_status_caixa.config(
                text=(
                    f"CAIXA ABERTO  •  Nº {caixa[0]}  •  "
                    f"Fundo: {moeda(caixa[2])}"
                ),
                bg=COR_SUCESSO_CLARO,
                fg=COR_SUCESSO
            )
        else:
            label_status_caixa.config(
                text="CAIXA FECHADO",
                bg=COR_PERIGO_CLARO,
                fg=COR_PERIGO
            )

    except Exception as erro:
        label_status_caixa.config(
            text="ERRO DE CONEXÃO",
            bg=COR_ALERTA_CLARO,
            fg=COR_ALERTA
        )
        messagebox.showerror(
            "SQL Server",
            f"Não foi possível consultar o caixa.\n\n{erro}"
        )

# ==========================================================
# ABRIR CAIXA
# ==========================================================

def abrir_caixa():
    try:
        caixa_atual = buscar_caixa_aberto()
    except Exception as erro:
        messagebox.showerror("SQL Server", str(erro))
        return

    if caixa_atual:
        messagebox.showwarning(
            "Caixa",
            f"O caixa Nº {caixa_atual[0]} já está aberto."
        )
        return

    tela, conteudo = criar_tela("Abrir Caixa", 500, 450)

    tk.Label(
        conteudo,
        text="ABRIR CAIXA",
        font=("Arial", 24, "bold")
    ).pack(pady=30)

    tk.Label(
        conteudo,
        text="Dinheiro físico inicial na gaveta:",
        font=("Arial", 14)
    ).pack()

    tk.Label(
        conteudo,
        text="Fundo de troco",
        font=("Arial", 11)
    ).pack(pady=5)

    entrada_valor = tk.Entry(
        conteudo,
        font=("Arial", 22),
        width=15,
        justify="center"
    )
    entrada_valor.pack(pady=15)

    def confirmar():
        try:
            valor = converter_valor(entrada_valor.get())
        except Exception:
            messagebox.showerror("Erro", "Digite um valor válido.")
            return

        if valor < Decimal("0.00"):
            messagebox.showerror("Erro", "O valor não pode ser negativo.")
            return

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                INSERT INTO dbo.caixas (
                    valor_inicial,
                    status
                )
                OUTPUT INSERTED.id
                VALUES (?, 'ABERTO')
            """, (valor,))

            caixa_id = cursor.fetchone()[0]
            conexao.commit()

        except Exception as erro:
            conexao.rollback()
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir o caixa.\n\n{erro}"
            )
            return

        finally:
            conexao.close()

        messagebox.showinfo(
            "Caixa aberto",
            f"CAIXA ABERTO COM SUCESSO!\n\n"
            f"Caixa Nº {caixa_id}\n"
            f"Fundo inicial: {moeda(valor)}"
        )

        atualizar_status_caixa()
        tela.destroy()

    tk.Button(
        conteudo,
        text="ABRIR CAIXA",
        font=("Arial", 16, "bold"),
        width=18,
        height=2,
        command=confirmar
    ).pack(pady=10)

    entrada_valor.bind("<Return>", lambda event: confirmar())
    entrada_valor.focus()


# ==========================================================
# FECHAR CAIXA
# ==========================================================

def fechar_caixa():
    try:
        caixa = buscar_caixa_aberto()
    except Exception as erro:
        messagebox.showerror("SQL Server", str(erro))
        return

    if not caixa:
        messagebox.showwarning("Caixa", "Não existe nenhum caixa aberto.")
        return

    caixa_id = caixa[0]
    valor_inicial = dinheiro(caixa[2])

    conexao = conectar()
    cursor = conexao.cursor()
    totais = {}

    try:
        for forma in ("Dinheiro", "PIX", "Débito", "Crédito"):
            cursor.execute("""
                SELECT COALESCE(SUM(valor_total), 0)
                FROM dbo.vendas
                WHERE
                    caixa_id = ?
                    AND forma_pagamento = ?
                    AND COALESCE(status, 'CONCLUIDA') = 'CONCLUIDA'
            """, (caixa_id, forma))

            totais[forma] = dinheiro(cursor.fetchone()[0])

        cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(valor_total), 0)
            FROM dbo.vendas
            WHERE
                caixa_id = ?
                AND COALESCE(status, 'CONCLUIDA') = 'CONCLUIDA'
        """, (caixa_id,))

        resumo = cursor.fetchone()

    except Exception as erro:
        messagebox.showerror("Erro", str(erro))
        return

    finally:
        conexao.close()

    quantidade_vendas = resumo[0]
    total_vendido = dinheiro(resumo[1])
    valor_esperado = dinheiro(valor_inicial + totais["Dinheiro"])

    tela, conteudo = criar_tela("Fechar Caixa", 700, 760)

    tk.Label(
        conteudo,
        text="FECHAMENTO DE CAIXA",
        font=("Arial", 24, "bold")
    ).pack(pady=20)

    tk.Label(
        conteudo,
        text=f"Caixa Nº {caixa_id}",
        font=("Arial", 14)
    ).pack()

    frame = tk.Frame(conteudo)
    frame.pack(pady=20)

    dados = [
        ("Fundo inicial:", moeda(valor_inicial)),
        ("Vendas em dinheiro:", moeda(totais["Dinheiro"])),
        ("Vendas em PIX:", moeda(totais["PIX"])),
        ("Vendas no débito:", moeda(totais["Débito"])),
        ("Vendas no crédito:", moeda(totais["Crédito"])),
        ("Quantidade de vendas:", str(quantidade_vendas))
    ]

    for linha, item in enumerate(dados):
        tk.Label(
            frame,
            text=item[0],
            font=("Arial", 13),
            anchor="e",
            width=24
        ).grid(row=linha, column=0, padx=10, pady=5)

        tk.Label(
            frame,
            text=item[1],
            font=("Arial", 13, "bold"),
            anchor="w",
            width=18
        ).grid(row=linha, column=1, padx=10, pady=5)

    tk.Label(
        conteudo,
        text="TOTAL VENDIDO",
        font=("Arial", 12)
    ).pack(pady=(10, 0))

    tk.Label(
        conteudo,
        text=moeda(total_vendido),
        font=("Arial", 28, "bold")
    ).pack()

    tk.Label(
        conteudo,
        text="DINHEIRO ESPERADO NA GAVETA",
        font=("Arial", 12)
    ).pack(pady=(20, 0))

    tk.Label(
        conteudo,
        text=moeda(valor_esperado),
        font=("Arial", 26, "bold")
    ).pack()

    tk.Label(
        conteudo,
        text="Quanto você contou fisicamente?",
        font=("Arial", 14)
    ).pack(pady=(20, 5))

    entrada_contado = tk.Entry(
        conteudo,
        font=("Arial", 22),
        width=15,
        justify="center"
    )
    entrada_contado.pack(pady=5)

    label_diferenca_titulo = tk.Label(
        conteudo,
        text="DIFERENÇA",
        font=("Arial", 12)
    )
    label_diferenca_titulo.pack(pady=(15, 0))

    label_diferenca = tk.Label(
        conteudo,
        text="R$ 0,00",
        font=("Arial", 26, "bold")
    )
    label_diferenca.pack()

    dados_fechamento = {"contado": None, "diferenca": None}

    def calcular():
        try:
            contado = converter_valor(entrada_contado.get())
        except Exception:
            messagebox.showerror("Erro", "Digite um valor válido.")
            return False

        if contado < Decimal("0.00"):
            messagebox.showerror(
                "Erro",
                "O valor contado não pode ser negativo."
            )
            return False

        diferenca = dinheiro(contado - valor_esperado)
        dados_fechamento["contado"] = contado
        dados_fechamento["diferenca"] = diferenca

        if diferenca == Decimal("0.00"):
            label_diferenca_titulo.config(text="CAIXA CORRETO")
            label_diferenca.config(text=moeda(0))
        elif diferenca > 0:
            label_diferenca_titulo.config(text="SOBRA DE CAIXA")
            label_diferenca.config(text=f"+ {moeda(diferenca)}")
        else:
            label_diferenca_titulo.config(text="FALTA DE CAIXA")
            label_diferenca.config(text=f"- {moeda(abs(diferenca))}")

        return True

    def confirmar_fechamento():
        if not calcular():
            return

        diferenca = dados_fechamento["diferenca"]

        if diferenca > 0:
            situacao = f"Sobra de {moeda(diferenca)}"
        elif diferenca < 0:
            situacao = f"Falta de {moeda(abs(diferenca))}"
        else:
            situacao = "Caixa correto"

        resposta = messagebox.askyesno(
            "Confirmar fechamento",
            f"Fechar o Caixa Nº {caixa_id}?\n\n"
            f"Total vendido: {moeda(total_vendido)}\n"
            f"Esperado na gaveta: {moeda(valor_esperado)}\n"
            f"Contado: {moeda(dados_fechamento['contado'])}\n"
            f"{situacao}"
        )

        if not resposta:
            return

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                UPDATE dbo.caixas
                SET
                    data_fechamento = SYSUTCDATETIME(),
                    valor_contado = ?,
                    valor_esperado = ?,
                    diferenca = ?,
                    status = 'FECHADO'
                WHERE
                    id = ?
                    AND status = 'ABERTO'
            """, (
                dados_fechamento["contado"],
                valor_esperado,
                diferenca,
                caixa_id
            ))

            if cursor.rowcount == 0:
                raise Exception("Esse caixa já foi fechado.")

            conexao.commit()

        except Exception as erro:
            conexao.rollback()
            messagebox.showerror(
                "Erro",
                f"Não foi possível fechar o caixa.\n\n{erro}"
            )
            return

        finally:
            conexao.close()

        messagebox.showinfo(
            "Caixa fechado",
            f"CAIXA Nº {caixa_id} FECHADO!\n\n"
            f"Total vendido: {moeda(total_vendido)}\n"
            f"{situacao}"
        )

        atualizar_status_caixa()
        tela.destroy()

    frame_botoes = tk.Frame(conteudo)
    frame_botoes.pack(pady=20)

    tk.Button(
        frame_botoes,
        text="CALCULAR",
        font=("Arial", 12),
        width=14,
        command=calcular
    ).pack(side="left", padx=8)

    tk.Button(
        frame_botoes,
        text="FECHAR CAIXA",
        font=("Arial", 14, "bold"),
        width=16,
        command=confirmar_fechamento
    ).pack(side="left", padx=8)

    entrada_contado.bind("<Return>", lambda event: calcular())
    entrada_contado.focus()


# ==========================================================
# VERIFICAR PREÇO
# ==========================================================

def abrir_verificar_preco():
    tela, conteudo = criar_tela("Verificar Preço", 550, 460)

    tk.Label(
        conteudo,
        text="VERIFICAR PREÇO",
        font=("Arial", 24, "bold")
    ).pack(pady=25)

    tk.Label(
        conteudo,
        text="Código de barras:",
        font=("Arial", 14)
    ).pack()

    entrada_codigo = tk.Entry(
        conteudo,
        font=("Arial", 18),
        width=25,
        justify="center"
    )
    entrada_codigo.pack(pady=10)

    label_nome = tk.Label(conteudo, text="", font=("Arial", 17))
    label_nome.pack(pady=10)

    label_preco = tk.Label(
        conteudo,
        text="",
        font=("Arial", 28, "bold")
    )
    label_preco.pack(pady=5)

    label_estoque = tk.Label(conteudo, text="", font=("Arial", 13))
    label_estoque.pack()

    def verificar():
        codigo = entrada_codigo.get().strip()
        if not codigo:
            return

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                SELECT nome, preco, estoque
                FROM dbo.produtos
                WHERE codigo_barras = ?
            """, (codigo,))
            produto = cursor.fetchone()

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return

        finally:
            conexao.close()

        if produto:
            label_nome.config(text=produto[0])
            label_preco.config(text=moeda(produto[1]))
            label_estoque.config(text=f"Estoque: {produto[2]} unidade(s)")
        else:
            label_nome.config(text="PRODUTO NÃO ENCONTRADO")
            label_preco.config(text="")
            label_estoque.config(text="")

        entrada_codigo.select_range(0, tk.END)
        entrada_codigo.focus()

    tk.Button(
        conteudo,
        text="VERIFICAR",
        font=("Arial", 14, "bold"),
        width=18,
        command=verificar
    ).pack(pady=18)

    entrada_codigo.bind("<Return>", lambda event: verificar())
    entrada_codigo.focus()


# ==========================================================
# PRODUTOS / ESTOQUE
# ==========================================================

def abrir_produtos():
    tela, conteudo = criar_tela("Produtos / Estoque", 1150, 760)
    produto_selecionado = {"id": None}

    tk.Label(
        conteudo,
        text="PRODUTOS / ESTOQUE",
        font=("Arial", 24, "bold")
    ).pack(pady=15)

    frame_formulario = tk.Frame(conteudo)
    frame_formulario.pack(pady=5)

    nomes_campos = [
        "Código de barras",
        "Nome",
        "Categoria",
        "Preço",
        "Estoque"
    ]

    for coluna, nome in enumerate(nomes_campos):
        tk.Label(frame_formulario, text=nome).grid(
            row=0,
            column=coluna,
            padx=5,
            sticky="w"
        )

    entrada_codigo = tk.Entry(frame_formulario, width=20, font=("Arial", 11))
    entrada_codigo.grid(row=1, column=0, padx=5)

    entrada_nome = tk.Entry(frame_formulario, width=28, font=("Arial", 11))
    entrada_nome.grid(row=1, column=1, padx=5)

    entrada_categoria = tk.Entry(frame_formulario, width=20, font=("Arial", 11))
    entrada_categoria.grid(row=1, column=2, padx=5)

    entrada_preco = tk.Entry(frame_formulario, width=12, font=("Arial", 11))
    entrada_preco.grid(row=1, column=3, padx=5)

    entrada_estoque = tk.Entry(frame_formulario, width=10, font=("Arial", 11))
    entrada_estoque.grid(row=1, column=4, padx=5)

    frame_botoes = tk.Frame(conteudo)
    frame_botoes.pack(pady=12)

    frame_pesquisa = tk.Frame(conteudo)
    frame_pesquisa.pack(pady=5)

    tk.Label(
        frame_pesquisa,
        text="Pesquisar:",
        font=("Arial", 11)
    ).pack(side="left", padx=5)

    entrada_pesquisa = tk.Entry(
        frame_pesquisa,
        width=40,
        font=("Arial", 12)
    )
    entrada_pesquisa.pack(side="left", padx=5)

    frame_tabela = tk.Frame(conteudo)
    frame_tabela.pack(padx=20, pady=10, fill="both", expand=True)

    colunas = ("id", "codigo", "nome", "categoria", "preco", "estoque")
    tabela = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        height=16
    )

    barra_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    barra_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=tabela.xview)

    tabela.configure(
        yscrollcommand=barra_y.set,
        xscrollcommand=barra_x.set
    )

    tabela.grid(row=0, column=0, sticky="nsew")
    barra_y.grid(row=0, column=1, sticky="ns")
    barra_x.grid(row=1, column=0, sticky="ew")
    frame_tabela.rowconfigure(0, weight=1)
    frame_tabela.columnconfigure(0, weight=1)

    cabecalhos = {
        "id": "ID",
        "codigo": "Código de barras",
        "nome": "Produto",
        "categoria": "Categoria",
        "preco": "Preço",
        "estoque": "Estoque"
    }

    for coluna, titulo in cabecalhos.items():
        tabela.heading(coluna, text=titulo)

    tabela.column("id", width=50, anchor="center")
    tabela.column("codigo", width=180, anchor="center")
    tabela.column("nome", width=280)
    tabela.column("categoria", width=170, anchor="center")
    tabela.column("preco", width=120, anchor="center")
    tabela.column("estoque", width=100, anchor="center")

    def limpar_campos():
        produto_selecionado["id"] = None
        for entrada in (
            entrada_codigo,
            entrada_nome,
            entrada_categoria,
            entrada_preco,
            entrada_estoque
        ):
            entrada.delete(0, tk.END)
        entrada_codigo.focus()

    def carregar_produtos(event=None):
        pesquisa = texto_normalizado(entrada_pesquisa.get())

        for linha in tabela.get_children():
            tabela.delete(linha)

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                SELECT
                    id,
                    codigo_barras,
                    nome,
                    categoria,
                    preco,
                    estoque
                FROM dbo.produtos
                ORDER BY nome
            """)
            produtos = cursor.fetchall()

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return

        finally:
            conexao.close()

        resultados = []

        if not pesquisa:
            resultados = produtos
        else:
            palavras_pesquisa = pesquisa.split()

            for produto in produtos:
                codigo = str(produto[1])
                nome = produto[2]
                categoria = produto[3] or ""

                nome_norm = texto_normalizado(nome)
                categoria_norm = texto_normalizado(categoria)
                texto_completo = f"{nome_norm} {categoria_norm} {codigo}"

                encontrou = all(
                    palavra in texto_completo
                    for palavra in palavras_pesquisa
                )

                if encontrou:
                    resultados.append(produto)
                    continue

                palavras_produto = nome_norm.split() + categoria_norm.split()
                encontrou_aprox = True

                for palavra_pesquisa in palavras_pesquisa:
                    melhor = 0
                    for palavra_produto in palavras_produto:
                        melhor = max(
                            melhor,
                            similaridade(palavra_pesquisa, palavra_produto)
                        )

                    if melhor < 0.60:
                        encontrou_aprox = False
                        break

                if encontrou_aprox:
                    resultados.append(produto)

        for produto in resultados:
            tabela.insert(
                "",
                "end",
                values=(
                    produto[0],
                    produto[1],
                    produto[2],
                    produto[3] or "",
                    moeda(produto[4]),
                    produto[5]
                )
            )

    def cadastrar_produto():
        codigo = entrada_codigo.get().strip()
        nome = entrada_nome.get().strip()
        categoria = entrada_categoria.get().strip()

        if not codigo or not nome:
            messagebox.showwarning(
                "Produto",
                "Código e nome são obrigatórios."
            )
            return

        try:
            preco = converter_valor(entrada_preco.get())
            estoque = int(entrada_estoque.get().strip())
        except Exception:
            messagebox.showerror("Erro", "Preço ou estoque inválido.")
            return

        if preco < Decimal("0.00") or estoque < 0:
            messagebox.showerror(
                "Erro",
                "Preço e estoque não podem ser negativos."
            )
            return

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                INSERT INTO dbo.produtos (
                    codigo_barras,
                    nome,
                    categoria,
                    preco,
                    estoque
                )
                VALUES (?, ?, ?, ?, ?)
            """, (codigo, nome, categoria, preco, estoque))

            conexao.commit()
            messagebox.showinfo("Produto", "Produto cadastrado com sucesso!")
            limpar_campos()
            carregar_produtos()

        except pyodbc.IntegrityError:
            conexao.rollback()
            messagebox.showerror("Erro", "Esse código de barras já existe.")

        except Exception as erro:
            conexao.rollback()
            messagebox.showerror("Erro", str(erro))

        finally:
            conexao.close()

    def selecionar_produto(event=None):
        selecionado = tabela.selection()
        if not selecionado:
            return

        valores = tabela.item(selecionado[0], "values")
        produto_selecionado["id"] = int(valores[0])

        entrada_codigo.delete(0, tk.END)
        entrada_codigo.insert(0, valores[1])

        entrada_nome.delete(0, tk.END)
        entrada_nome.insert(0, valores[2])

        entrada_categoria.delete(0, tk.END)
        entrada_categoria.insert(0, valores[3])

        preco = (
            valores[4]
            .replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

        entrada_preco.delete(0, tk.END)
        entrada_preco.insert(0, preco)

        entrada_estoque.delete(0, tk.END)
        entrada_estoque.insert(0, valores[5])

    def atualizar_produto():
        produto_id = produto_selecionado["id"]

        if produto_id is None:
            messagebox.showwarning("Produto", "Selecione um produto.")
            return

        codigo = entrada_codigo.get().strip()
        nome = entrada_nome.get().strip()
        categoria = entrada_categoria.get().strip()

        if not codigo or not nome:
            messagebox.showwarning(
                "Produto",
                "Código e nome são obrigatórios."
            )
            return

        try:
            preco = converter_valor(entrada_preco.get())
            estoque = int(entrada_estoque.get().strip())
        except Exception:
            messagebox.showerror("Erro", "Preço ou estoque inválido.")
            return

        if preco < Decimal("0.00") or estoque < 0:
            messagebox.showerror(
                "Erro",
                "Preço e estoque não podem ser negativos."
            )
            return

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                UPDATE dbo.produtos
                SET
                    codigo_barras = ?,
                    nome = ?,
                    categoria = ?,
                    preco = ?,
                    estoque = ?
                WHERE id = ?
            """, (
                codigo,
                nome,
                categoria,
                preco,
                estoque,
                produto_id
            ))

            conexao.commit()
            messagebox.showinfo("Produto", "Produto atualizado!")
            limpar_campos()
            carregar_produtos()

        except pyodbc.IntegrityError:
            conexao.rollback()
            messagebox.showerror("Erro", "Código de barras já utilizado.")

        except Exception as erro:
            conexao.rollback()
            messagebox.showerror("Erro", str(erro))

        finally:
            conexao.close()

    tk.Button(
        frame_botoes,
        text="CADASTRAR NOVO",
        font=("Arial", 11, "bold"),
        width=18,
        command=cadastrar_produto
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes,
        text="SALVAR ALTERAÇÕES",
        font=("Arial", 11, "bold"),
        width=18,
        command=atualizar_produto
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes,
        text="LIMPAR",
        font=("Arial", 11),
        width=12,
        command=limpar_campos
    ).pack(side="left", padx=5)

    def mostrar_todos():
        entrada_pesquisa.delete(0, tk.END)
        carregar_produtos()

    tk.Button(
        frame_pesquisa,
        text="MOSTRAR TODOS",
        command=mostrar_todos
    ).pack(side="left", padx=5)

    entrada_pesquisa.bind("<KeyRelease>", carregar_produtos)
    tabela.bind("<<TreeviewSelect>>", selecionar_produto)
    carregar_produtos()


# ==========================================================
# CANCELAMENTO DE VENDA
# ==========================================================

def cancelar_venda(venda_id, ao_concluir=None):
    try:
        caixa_aberto = buscar_caixa_aberto()
    except Exception as erro:
        messagebox.showerror("SQL Server", str(erro))
        return False

    if not caixa_aberto:
        messagebox.showwarning(
            "Cancelamento",
            "Para cancelar uma venda, o caixa correspondente precisa estar aberto.\n\n"
            "Vendas de caixas já fechados devem ser tratadas depois como estorno/devolução."
        )
        return False

    motivo = simpledialog.askstring(
        "Cancelar venda",
        f"Informe o motivo do cancelamento da venda Nº {venda_id}:"
    )

    if motivo is None:
        return False

    motivo = motivo.strip()

    if not motivo:
        messagebox.showwarning(
            "Cancelamento",
            "O motivo do cancelamento é obrigatório."
        )
        return False

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT
                id,
                caixa_id,
                valor_total,
                forma_pagamento,
                COALESCE(status, 'CONCLUIDA')
            FROM dbo.vendas WITH (UPDLOCK, ROWLOCK)
            WHERE id = ?
        """, (venda_id,))

        venda = cursor.fetchone()

        if not venda:
            raise Exception("Venda não encontrada.")

        if venda[4] == "CANCELADA":
            raise Exception("Essa venda já está cancelada.")

        if venda[1] != caixa_aberto[0]:
            raise Exception(
                "Essa venda pertence a outro caixa ou a um caixa já fechado.\n\n"
                "O cancelamento simples só pode ser feito no mesmo caixa ainda aberto."
            )

        resposta = messagebox.askyesno(
            "Confirmar cancelamento",
            f"Cancelar a venda Nº {venda_id}?\n\n"
            f"Total: {moeda(venda[2])}\n"
            f"Pagamento: {venda[3]}\n"
            f"Motivo: {motivo}\n\n"
            "Os produtos voltarão para o estoque."
        )

        if not resposta:
            conexao.rollback()
            return False

        cursor.execute("""
            SELECT
                produto_id,
                quantidade
            FROM dbo.itens_venda
            WHERE venda_id = ?
        """, (venda_id,))

        itens = cursor.fetchall()

        for item in itens:
            cursor.execute("""
                UPDATE dbo.produtos
                SET estoque = estoque + ?
                WHERE id = ?
            """, (item[1], item[0]))

            if cursor.rowcount == 0:
                raise Exception(
                    f"Não foi possível devolver ao estoque o produto ID {item[0]}."
                )

        cursor.execute("""
            UPDATE dbo.vendas
            SET
                status = 'CANCELADA',
                data_cancelamento = SYSUTCDATETIME(),
                motivo_cancelamento = ?
            WHERE
                id = ?
                AND COALESCE(status, 'CONCLUIDA') <> 'CANCELADA'
        """, (motivo, venda_id))

        if cursor.rowcount == 0:
            raise Exception("A venda não pôde ser cancelada.")

        conexao.commit()

    except Exception as erro:
        conexao.rollback()
        messagebox.showerror(
            "Cancelamento",
            f"Não foi possível cancelar a venda.\n\n{erro}"
        )
        return False

    finally:
        conexao.close()

    messagebox.showinfo(
        "Venda cancelada",
        f"VENDA Nº {venda_id} CANCELADA!\n\n"
        "Os itens foram devolvidos ao estoque.\n"
        "A venda continuará aparecendo no histórico como CANCELADA."
    )

    if ao_concluir:
        ao_concluir()

    return True


# ==========================================================
# DETALHES DA VENDA
# ==========================================================

def abrir_detalhes_venda(venda_id):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT
                data,
                valor_total,
                forma_pagamento,
                valor_recebido,
                troco,
                caixa_id,
                COALESCE(status, 'CONCLUIDA'),
                data_cancelamento,
                motivo_cancelamento
            FROM dbo.vendas
            WHERE id = ?
        """, (venda_id,))

        venda = cursor.fetchone()

        cursor.execute("""
            SELECT
                p.nome,
                iv.quantidade,
                iv.preco_unitario,
                iv.subtotal
            FROM dbo.itens_venda iv
            INNER JOIN dbo.produtos p
                ON p.id = iv.produto_id
            WHERE iv.venda_id = ?
            ORDER BY iv.id
        """, (venda_id,))

        itens = cursor.fetchall()

    except Exception as erro:
        messagebox.showerror("Erro", str(erro))
        return

    finally:
        conexao.close()

    if not venda:
        messagebox.showerror("Venda", "Venda não encontrada.")
        return

    tela, conteudo = criar_tela(f"Venda Nº {venda_id}", 850, 700)

    tk.Label(
        conteudo,
        text=f"VENDA Nº {venda_id}",
        font=("Arial", 24, "bold")
    ).pack(pady=15)

    status = venda[6]

    tk.Label(
        conteudo,
        text=f"STATUS: {status}",
        font=("Arial", 14, "bold")
    ).pack(pady=5)

    tk.Label(
        conteudo,
        text=(
            f"Data: {formatar_data_local(venda[0])}\n"
            f"Pagamento: {venda[2]}\n"
            f"Total: {moeda(venda[1])}\n"
            f"Caixa: {venda[5] or '-'}"
        ),
        font=("Arial", 12),
        justify="center"
    ).pack(pady=5)

    if venda[2] == "Dinheiro":
        tk.Label(
            conteudo,
            text=(
                f"Recebido: {moeda(venda[3])}   |   "
                f"Troco: {moeda(venda[4])}"
            ),
            font=("Arial", 12)
        ).pack(pady=5)

    if status == "CANCELADA":
        tk.Label(
            conteudo,
            text=(
                f"Cancelada em: {formatar_data_local(venda[7])}\n"
                f"Motivo: {venda[8] or '-'}"
            ),
            font=("Arial", 12, "bold"),
            justify="center"
        ).pack(pady=10)

    frame_tabela = tk.Frame(conteudo)
    frame_tabela.pack(padx=20, pady=20, fill="both", expand=True)

    tabela = ttk.Treeview(
        frame_tabela,
        columns=("produto", "qtd", "preco", "subtotal"),
        show="headings",
        height=14
    )

    barra_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    barra_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=tabela.xview)

    tabela.configure(
        yscrollcommand=barra_y.set,
        xscrollcommand=barra_x.set
    )

    tabela.grid(row=0, column=0, sticky="nsew")
    barra_y.grid(row=0, column=1, sticky="ns")
    barra_x.grid(row=1, column=0, sticky="ew")
    frame_tabela.rowconfigure(0, weight=1)
    frame_tabela.columnconfigure(0, weight=1)

    tabela.heading("produto", text="Produto")
    tabela.heading("qtd", text="Qtd")
    tabela.heading("preco", text="Preço")
    tabela.heading("subtotal", text="Subtotal")

    tabela.column("produto", width=300)
    tabela.column("qtd", width=80, anchor="center")
    tabela.column("preco", width=130, anchor="center")
    tabela.column("subtotal", width=130, anchor="center")

    for item in itens:
        tabela.insert(
            "",
            "end",
            values=(
                item[0],
                item[1],
                moeda(item[2]),
                moeda(item[3])
            )
        )


# ==========================================================
# HISTÓRICO
# ==========================================================

def abrir_historico():
    tela, conteudo = criar_tela("Histórico", 1200, 760)

    tk.Label(
        conteudo,
        text="HISTÓRICO DE VENDAS",
        font=(FONTE, 24, "bold"),
        bg=COR_FUNDO,
        fg=COR_TEXTO
    ).pack(pady=(20, 8))

    tk.Label(
        conteudo,
        text="Filtre por período ou use os atalhos. Dê dois cliques em uma venda para ver os detalhes.",
        font=(FONTE, 10),
        bg=COR_FUNDO,
        fg=COR_TEXTO_SECUNDARIO
    ).pack(pady=(0, 12))

    frame_filtro = criar_card(conteudo, padx=16, pady=14)
    frame_filtro.pack(padx=20, pady=(0, 12), fill="x")

    hoje = datetime.now().astimezone()
    inicio_padrao = hoje - timedelta(days=6)

    tk.Label(frame_filtro, text="De", bg=COR_CARD, fg=COR_TEXTO_SECUNDARIO,
             font=(FONTE, 10, "bold")).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="w")
    entrada_de = tk.Entry(frame_filtro, width=12, font=(FONTE, 11), justify="center")
    entrada_de.grid(row=0, column=1, padx=(0, 12), pady=4)
    entrada_de.insert(0, formatar_data_filtro(inicio_padrao))

    tk.Label(frame_filtro, text="Até", bg=COR_CARD, fg=COR_TEXTO_SECUNDARIO,
             font=(FONTE, 10, "bold")).grid(row=0, column=2, padx=(0, 6), pady=4, sticky="w")
    entrada_ate = tk.Entry(frame_filtro, width=12, font=(FONTE, 11), justify="center")
    entrada_ate.grid(row=0, column=3, padx=(0, 12), pady=4)
    entrada_ate.insert(0, formatar_data_filtro(hoje))

    label_periodo = tk.Label(
        frame_filtro,
        text="",
        bg=COR_CARD,
        fg=COR_TEXTO_SECUNDARIO,
        font=(FONTE, 9)
    )
    label_periodo.grid(row=1, column=0, columnspan=8, sticky="w", pady=(8, 0))

    frame_tabela = tk.Frame(conteudo, bg=COR_CARD)
    frame_tabela.pack(padx=20, pady=8, fill="both", expand=True)

    tabela = ttk.Treeview(
        frame_tabela,
        columns=("id", "data", "total", "pagamento", "caixa", "status"),
        show="headings",
        height=18
    )

    barra_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    barra_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=tabela.xview)

    tabela.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
    tabela.grid(row=0, column=0, sticky="nsew")
    barra_y.grid(row=0, column=1, sticky="ns")
    barra_x.grid(row=1, column=0, sticky="ew")
    frame_tabela.rowconfigure(0, weight=1)
    frame_tabela.columnconfigure(0, weight=1)

    tabela.heading("id", text="Venda")
    tabela.heading("data", text="Data")
    tabela.heading("total", text="Total")
    tabela.heading("pagamento", text="Pagamento")
    tabela.heading("caixa", text="Caixa")
    tabela.heading("status", text="Status")

    tabela.column("id", width=80, anchor="center")
    tabela.column("data", width=220, anchor="center")
    tabela.column("total", width=150, anchor="center")
    tabela.column("pagamento", width=160, anchor="center")
    tabela.column("caixa", width=100, anchor="center")
    tabela.column("status", width=140, anchor="center")
    tabela.tag_configure("cancelada", foreground="#777777")

    def definir_periodo(data_de, data_ate=None):
        if data_ate is None:
            data_ate = data_de
        entrada_de.delete(0, tk.END)
        entrada_de.insert(0, formatar_data_filtro(data_de))
        entrada_ate.delete(0, tk.END)
        entrada_ate.insert(0, formatar_data_filtro(data_ate))
        carregar()

    def carregar():
        try:
            data_de = datetime.strptime(entrada_de.get().strip(), "%d/%m/%Y")
            data_ate = datetime.strptime(entrada_ate.get().strip(), "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Data", "Use o formato DD/MM/AAAA. Exemplo: 05/09/2026")
            return

        if data_ate.date() < data_de.date():
            messagebox.showwarning("Período", "A data final não pode ser anterior à data inicial.")
            return

        inicio_utc, _ = limites_data_local_utc(data_de)
        _, fim_utc = limites_data_local_utc(data_ate)

        for item in tabela.get_children():
            tabela.delete(item)

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                SELECT
                    id, data, valor_total, forma_pagamento, caixa_id,
                    COALESCE(status, 'CONCLUIDA')
                FROM dbo.vendas
                WHERE data >= ? AND data < ?
                ORDER BY id DESC
            """, (inicio_utc, fim_utc))
            vendas = cursor.fetchall()
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        finally:
            conexao.close()

        for venda in vendas:
            tags = ("cancelada",) if venda[5] == "CANCELADA" else ()
            tabela.insert(
                "", "end",
                values=(
                    venda[0], formatar_data_local(venda[1]), moeda(venda[2]),
                    venda[3], venda[4] or "-", venda[5]
                ),
                tags=tags
            )

        label_periodo.config(
            text=(
                f"Período: {data_de.strftime('%d/%m/%Y')} a {data_ate.strftime('%d/%m/%Y')}  •  "
                f"{len(vendas)} venda(s) encontrada(s)"
            )
        )

    botao_moderno(frame_filtro, "FILTRAR", carregar, padx=14, pady=8).grid(row=0, column=4, padx=5)
    botao_moderno(
        frame_filtro, "HOJE",
        lambda: definir_periodo(datetime.now().astimezone()),
        cor="#475569", cor_ativa="#334155", padx=12, pady=8
    ).grid(row=0, column=5, padx=5)
    botao_moderno(
        frame_filtro, "ÚLTIMOS 7 DIAS",
        lambda: definir_periodo(datetime.now().astimezone() - timedelta(days=6), datetime.now().astimezone()),
        cor="#475569", cor_ativa="#334155", padx=12, pady=8
    ).grid(row=0, column=6, padx=5)

    def venda_selecionada():
        selecionado = tabela.selection()
        if not selecionado:
            messagebox.showwarning("Histórico", "Selecione uma venda.")
            return None
        valores = tabela.item(selecionado[0], "values")
        return int(valores[0]), valores[5]

    def detalhes(event=None):
        selecionada = venda_selecionada()
        if selecionada:
            abrir_detalhes_venda(selecionada[0])

    def cancelar_selecionada():
        selecionada = venda_selecionada()
        if not selecionada:
            return
        venda_id, status = selecionada
        if status == "CANCELADA":
            messagebox.showwarning("Cancelamento", "Essa venda já está cancelada.")
            return
        cancelar_venda(venda_id, ao_concluir=carregar)

    tabela.bind("<Double-1>", detalhes)
    entrada_de.bind("<Return>", lambda event: carregar())
    entrada_ate.bind("<Return>", lambda event: carregar())

    frame_botoes = tk.Frame(conteudo, bg=COR_FUNDO)
    frame_botoes.pack(pady=10)
    botao_moderno(frame_botoes, "VER DETALHES", detalhes, padx=16, pady=9).pack(side="left", padx=5)
    botao_moderno(
        frame_botoes, "CANCELAR VENDA", cancelar_selecionada,
        cor=COR_PERIGO, cor_ativa=COR_PERIGO_HOVER, padx=16, pady=9
    ).pack(side="left", padx=5)
    botao_moderno(
        frame_botoes, "ATUALIZAR", carregar,
        cor="#475569", cor_ativa="#334155", padx=16, pady=9
    ).pack(side="left", padx=5)

    carregar()


# ==========================================================
# RELATÓRIOS
# ==========================================================

def abrir_relatorios():
    tela, conteudo = criar_tela("Relatórios", 1050, 800)

    titulo_relatorio = tk.Label(
        conteudo,
        text="RELATÓRIO DE VENDAS",
        font=(FONTE, 24, "bold"),
        bg=COR_FUNDO,
        fg=COR_TEXTO
    )
    titulo_relatorio.pack(pady=(20, 8))

    frame_filtro = criar_card(conteudo, padx=16, pady=14)
    frame_filtro.pack(padx=20, pady=(0, 12), fill="x")

    data_atual = {"valor": datetime.now().astimezone()}

    tk.Label(
        frame_filtro, text="Data do relatório", bg=COR_CARD, fg=COR_TEXTO_SECUNDARIO,
        font=(FONTE, 10, "bold")
    ).pack(side="left", padx=(0, 8))

    entrada_data = tk.Entry(frame_filtro, width=12, font=(FONTE, 11), justify="center")
    entrada_data.pack(side="left", padx=(0, 10))
    entrada_data.insert(0, formatar_data_filtro(data_atual["valor"]))

    frame = tk.Frame(conteudo, bg=COR_FUNDO)
    frame.pack(padx=20, pady=10, fill="x")
    frame.columnconfigure((0, 1, 2), weight=1)

    def criar_card_indicador(coluna, titulo):
        card = criar_card(frame, padx=18, pady=14)
        card.grid(row=0, column=coluna, padx=6, sticky="ew")
        tk.Label(
            card, text=titulo, bg=COR_CARD, fg=COR_TEXTO_SECUNDARIO,
            font=(FONTE, 10, "bold")
        ).pack(anchor="w")
        valor = tk.Label(
            card, text="-", bg=COR_CARD, fg=COR_TEXTO,
            font=(FONTE, 20, "bold")
        )
        valor.pack(anchor="w", pady=(4, 0))
        return valor

    label_vendas = criar_card_indicador(0, "Vendas")
    label_faturamento = criar_card_indicador(1, "Faturamento")
    label_produtos = criar_card_indicador(2, "Produtos vendidos")

    frame_tabela = tk.Frame(conteudo, bg=COR_CARD)
    frame_tabela.pack(padx=20, pady=12, fill="both", expand=True)

    tabela = ttk.Treeview(
        frame_tabela, columns=("produto", "qtd", "total"),
        show="headings", height=14
    )
    barra_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    barra_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=tabela.xview)
    tabela.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
    tabela.grid(row=0, column=0, sticky="nsew")
    barra_y.grid(row=0, column=1, sticky="ns")
    barra_x.grid(row=1, column=0, sticky="ew")
    frame_tabela.rowconfigure(0, weight=1)
    frame_tabela.columnconfigure(0, weight=1)

    tabela.heading("produto", text="Produto")
    tabela.heading("qtd", text="Qtd")
    tabela.heading("total", text="Faturamento")
    tabela.column("produto", width=350)
    tabela.column("qtd", width=120, anchor="center")
    tabela.column("total", width=180, anchor="center")

    def carregar():
        try:
            data_escolhida = datetime.strptime(entrada_data.get().strip(), "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Data", "Use o formato DD/MM/AAAA. Exemplo: 05/09/2026")
            return

        data_atual["valor"] = data_escolhida
        inicio_utc, fim_utc = limites_data_local_utc(data_escolhida)
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(valor_total), 0)
                FROM dbo.vendas
                WHERE data >= ? AND data < ?
                  AND COALESCE(status, 'CONCLUIDA') = 'CONCLUIDA'
            """, (inicio_utc, fim_utc))
            resumo = cursor.fetchone()

            cursor.execute("""
                SELECT COALESCE(SUM(iv.quantidade), 0)
                FROM dbo.itens_venda iv
                INNER JOIN dbo.vendas v ON v.id = iv.venda_id
                WHERE v.data >= ? AND v.data < ?
                  AND COALESCE(v.status, 'CONCLUIDA') = 'CONCLUIDA'
            """, (inicio_utc, fim_utc))
            quantidade_produtos = cursor.fetchone()[0]

            cursor.execute("""
                SELECT p.nome, SUM(iv.quantidade), SUM(iv.subtotal)
                FROM dbo.itens_venda iv
                INNER JOIN dbo.produtos p ON p.id = iv.produto_id
                INNER JOIN dbo.vendas v ON v.id = iv.venda_id
                WHERE v.data >= ? AND v.data < ?
                  AND COALESCE(v.status, 'CONCLUIDA') = 'CONCLUIDA'
                GROUP BY p.id, p.nome
                ORDER BY SUM(iv.quantidade) DESC, SUM(iv.subtotal) DESC
            """, (inicio_utc, fim_utc))
            ranking = cursor.fetchall()
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        finally:
            conexao.close()

        titulo_relatorio.config(text=f"RELATÓRIO • {data_escolhida.strftime('%d/%m/%Y')}")
        label_vendas.config(text=str(resumo[0]))
        label_faturamento.config(text=moeda(resumo[1]))
        label_produtos.config(text=str(quantidade_produtos))

        for item in tabela.get_children():
            tabela.delete(item)
        for produto in ranking:
            tabela.insert("", "end", values=(produto[0], produto[1], moeda(produto[2])))

    def mudar_dia(delta):
        try:
            atual = datetime.strptime(entrada_data.get().strip(), "%d/%m/%Y")
        except ValueError:
            atual = datetime.now().astimezone()
        nova = atual + timedelta(days=delta)
        entrada_data.delete(0, tk.END)
        entrada_data.insert(0, formatar_data_filtro(nova))
        carregar()

    def ir_para(data):
        entrada_data.delete(0, tk.END)
        entrada_data.insert(0, formatar_data_filtro(data))
        carregar()

    botao_moderno(
        frame_filtro, "◀ DIA ANTERIOR", lambda: mudar_dia(-1),
        cor="#475569", cor_ativa="#334155", padx=12, pady=8
    ).pack(side="left", padx=4)
    botao_moderno(
        frame_filtro, "HOJE", lambda: ir_para(datetime.now().astimezone()),
        cor="#475569", cor_ativa="#334155", padx=12, pady=8
    ).pack(side="left", padx=4)
    botao_moderno(frame_filtro, "VER RELATÓRIO", carregar, padx=14, pady=8).pack(side="left", padx=4)
    botao_moderno(
        frame_filtro, "PRÓXIMO DIA ▶", lambda: mudar_dia(1),
        cor="#475569", cor_ativa="#334155", padx=12, pady=8
    ).pack(side="left", padx=4)

    entrada_data.bind("<Return>", lambda event: carregar())
    carregar()


# ==========================================================
# VENDA
# ==========================================================

def abrir_venda():
    try:
        caixa = buscar_caixa_aberto()
    except Exception as erro:
        messagebox.showerror("SQL Server", str(erro))
        return

    if not caixa:
        messagebox.showwarning(
            "Caixa fechado",
            "Você precisa ABRIR O CAIXA antes de realizar vendas."
        )
        return

    caixa_id = caixa[0]
    tela, conteudo = criar_tela("Venda", 1280, 800)
    carrinho = []

    # ---------- Cabeçalho ----------
    topo = tk.Frame(conteudo, bg=COR_CABECALHO, padx=26, pady=18)
    topo.pack(fill="x")
    topo.columnconfigure(0, weight=1)

    tk.Label(
        topo,
        text="NOVA VENDA",
        font=(FONTE, 23, "bold"),
        bg=COR_CABECALHO,
        fg="#FFFFFF"
    ).grid(row=0, column=0, sticky="w")

    tk.Label(
        topo,
        text=f"Caixa Nº {caixa_id}  •  Venda em andamento",
        font=(FONTE, 10),
        bg=COR_CABECALHO,
        fg="#CBD5E1"
    ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    tk.Label(
        topo,
        text="CAIXA OCUPADO",
        font=(FONTE, 10, "bold"),
        bg="#1E293B",
        fg="#FFFFFF",
        padx=14,
        pady=8
    ).grid(row=0, column=1, rowspan=2, sticky="e")

    # Pequena faixa de etapas, inspirada em telas de PDV.
    etapas = tk.Frame(conteudo, bg=COR_CARD, padx=26, pady=10)
    etapas.pack(fill="x")
    for coluna, (texto, ativo) in enumerate([
        ("1  PRODUTO", True),
        ("2  ITENS DA VENDA", True),
        ("3  FINALIZAÇÃO", False),
    ]):
        tk.Label(
            etapas,
            text=texto,
            font=(FONTE, 10, "bold"),
            bg=COR_CARD,
            fg=COR_PRIMARIA if ativo else COR_TEXTO_SECUNDARIO,
            padx=18,
            pady=6
        ).grid(row=0, column=coluna, sticky="w")

    corpo = tk.Frame(conteudo, bg=COR_FUNDO, padx=24, pady=22)
    corpo.pack(fill="both", expand=True)
    corpo.columnconfigure(0, weight=4, uniform="venda")
    corpo.columnconfigure(1, weight=7, uniform="venda")
    corpo.rowconfigure(0, weight=1)

    # ---------- Coluna esquerda: produto ----------
    painel_produto = criar_card(corpo, padx=24, pady=22)
    painel_produto.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    painel_produto.columnconfigure(0, weight=1)

    tk.Label(
        painel_produto,
        text="Adicionar produto",
        font=(FONTE, 16, "bold"),
        bg=COR_CARD,
        fg=COR_TEXTO
    ).grid(row=0, column=0, sticky="w")

    tk.Label(
        painel_produto,
        text="Digite ou leia o código de barras do item.",
        font=(FONTE, 10),
        bg=COR_CARD,
        fg=COR_TEXTO_SECUNDARIO
    ).grid(row=1, column=0, sticky="w", pady=(4, 20))

    tk.Label(
        painel_produto,
        text="Código de barras",
        font=(FONTE, 10, "bold"),
        bg=COR_CARD,
        fg=COR_TEXTO
    ).grid(row=2, column=0, sticky="w", pady=(0, 7))

    entrada_codigo = tk.Entry(
        painel_produto,
        font=(FONTE, 15),
        bg="#FFFFFF",
        fg=COR_TEXTO,
        insertbackground=COR_TEXTO,
        relief="flat",
        highlightthickness=1,
        highlightbackground=COR_BORDA,
        highlightcolor=COR_PRIMARIA
    )
    entrada_codigo.grid(row=3, column=0, sticky="ew", ipady=11)

    dica = tk.Frame(painel_produto, bg="#EFF6FF", padx=14, pady=12)
    dica.grid(row=4, column=0, sticky="ew", pady=(18, 14))
    tk.Label(
        dica,
        text="Leitor de código",
        font=(FONTE, 10, "bold"),
        bg="#EFF6FF",
        fg="#1E40AF"
    ).pack(anchor="w")
    tk.Label(
        dica,
        text="Ao pressionar Enter, o produto é incluído automaticamente.",
        font=(FONTE, 9),
        bg="#EFF6FF",
        fg="#475569",
        wraplength=300,
        justify="left"
    ).pack(anchor="w", pady=(3, 0))

    # Botão é criado depois da função adicionar.
    area_adicionar = tk.Frame(painel_produto, bg=COR_CARD)
    area_adicionar.grid(row=5, column=0, sticky="ew", pady=(4, 0))

    # ---------- Coluna direita: itens ----------
    painel_itens = criar_card(corpo, padx=0, pady=0)
    painel_itens.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    painel_itens.columnconfigure(0, weight=1)
    painel_itens.rowconfigure(1, weight=1)

    cabecalho_itens = tk.Frame(painel_itens, bg=COR_CARD, padx=22, pady=18)
    cabecalho_itens.grid(row=0, column=0, sticky="ew")
    cabecalho_itens.columnconfigure(0, weight=1)

    tk.Label(
        cabecalho_itens,
        text="Itens da venda",
        font=(FONTE, 16, "bold"),
        bg=COR_CARD,
        fg=COR_TEXTO
    ).grid(row=0, column=0, sticky="w")

    label_itens = tk.Label(
        cabecalho_itens,
        text="0 itens",
        font=(FONTE, 10, "bold"),
        bg="#EEF2FF",
        fg="#3730A3",
        padx=12,
        pady=6
    )
    label_itens.grid(row=0, column=1, sticky="e")

    frame_tabela = tk.Frame(painel_itens, bg=COR_CARD)
    frame_tabela.grid(row=1, column=0, sticky="nsew", padx=1)
    frame_tabela.rowconfigure(0, weight=1)
    frame_tabela.columnconfigure(0, weight=1)

    tabela = ttk.Treeview(
        frame_tabela,
        columns=("produto", "qtd", "preco", "subtotal"),
        show="headings",
        height=13
    )

    barra_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra_y.set)

    tabela.grid(row=0, column=0, sticky="nsew")
    barra_y.grid(row=0, column=1, sticky="ns")

    tabela.heading("produto", text="Produto")
    tabela.heading("qtd", text="Qtd")
    tabela.heading("preco", text="Preço")
    tabela.heading("subtotal", text="Subtotal")

    tabela.column("produto", width=360, minwidth=220)
    tabela.column("qtd", width=70, minwidth=60, anchor="center")
    tabela.column("preco", width=120, minwidth=100, anchor="center")
    tabela.column("subtotal", width=130, minwidth=110, anchor="center")

    rodape = tk.Frame(painel_itens, bg="#F8FAFC", padx=22, pady=18)
    rodape.grid(row=2, column=0, sticky="ew")
    rodape.columnconfigure(0, weight=1)

    tk.Label(
        rodape,
        text="TOTAL DA VENDA",
        font=(FONTE, 9, "bold"),
        bg="#F8FAFC",
        fg=COR_TEXTO_SECUNDARIO
    ).grid(row=0, column=0, sticky="w")

    label_total = tk.Label(
        rodape,
        text="R$ 0,00",
        font=(FONTE, 27, "bold"),
        bg="#F8FAFC",
        fg=COR_TEXTO
    )
    label_total.grid(row=1, column=0, sticky="w", pady=(2, 0))

    area_acoes = tk.Frame(rodape, bg="#F8FAFC")
    area_acoes.grid(row=0, column=1, rowspan=2, sticky="e")

    def calcular_total():
        return dinheiro(
            sum(
                (item["subtotal"] for item in carrinho),
                Decimal("0.00")
            )
        )

    def atualizar():
        for linha in tabela.get_children():
            tabela.delete(linha)

        quantidade_total = 0
        for indice, item in enumerate(carrinho):
            quantidade_total += item["quantidade"]
            tabela.insert(
                "",
                "end",
                iid=str(indice),
                values=(
                    item["nome"],
                    item["quantidade"],
                    moeda(item["preco"]),
                    moeda(item["subtotal"])
                )
            )

        label_total.config(text=moeda(calcular_total()))
        label_itens.config(
            text=f"{quantidade_total} item" if quantidade_total == 1
            else f"{quantidade_total} itens"
        )

    def adicionar():
        codigo = entrada_codigo.get().strip()
        if not codigo:
            entrada_codigo.focus()
            return

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                SELECT id, nome, preco, estoque
                FROM dbo.produtos
                WHERE codigo_barras = ?
            """, (codigo,))
            produto = cursor.fetchone()

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return

        finally:
            conexao.close()

        if not produto:
            messagebox.showerror("Venda", "Produto não encontrado.")
            entrada_codigo.delete(0, tk.END)
            entrada_codigo.focus()
            return

        produto_id = produto[0]
        nome = produto[1]
        preco = dinheiro(produto[2])
        estoque = produto[3]

        if estoque <= 0:
            messagebox.showwarning("Estoque", "Produto sem estoque.")
            entrada_codigo.select_range(0, tk.END)
            entrada_codigo.focus()
            return

        for item in carrinho:
            if item["id"] == produto_id:
                if item["quantidade"] >= estoque:
                    messagebox.showwarning("Estoque", "Estoque insuficiente.")
                    return

                item["quantidade"] += 1
                item["subtotal"] = dinheiro(
                    item["preco"] * item["quantidade"]
                )

                atualizar()
                entrada_codigo.delete(0, tk.END)
                entrada_codigo.focus()
                return

        carrinho.append({
            "id": produto_id,
            "nome": nome,
            "preco": preco,
            "quantidade": 1,
            "subtotal": preco
        })

        atualizar()
        entrada_codigo.delete(0, tk.END)
        entrada_codigo.focus()

    def remover():
        selecionado = tabela.selection()
        if not selecionado:
            messagebox.showwarning("Venda", "Selecione um produto.")
            return

        carrinho.pop(int(selecionado[0]))
        atualizar()

    def registrar(forma, recebido=None, troco=Decimal("0.00")):
        try:
            caixa_atual = buscar_caixa_aberto()
        except Exception as erro:
            messagebox.showerror("Caixa", str(erro))
            return None

        if not caixa_atual:
            messagebox.showerror(
                "Caixa",
                "O caixa foi fechado. A venda não pode ser concluída."
            )
            return None

        total = calcular_total()
        recebido = dinheiro(recebido) if recebido is not None else None
        troco = dinheiro(troco)

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            for item in carrinho:
                cursor.execute("""
                    SELECT estoque
                    FROM dbo.produtos WITH (UPDLOCK, ROWLOCK)
                    WHERE id = ?
                """, (item["id"],))

                estoque = cursor.fetchone()

                if estoque is None:
                    raise Exception(f'Produto "{item["nome"]}" não existe mais.')

                if estoque[0] < item["quantidade"]:
                    raise Exception(f'Estoque insuficiente para {item["nome"]}.')

            cursor.execute("""
                INSERT INTO dbo.vendas (
                    valor_total,
                    forma_pagamento,
                    valor_recebido,
                    troco,
                    caixa_id,
                    status
                )
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, 'CONCLUIDA')
            """, (
                total,
                forma,
                recebido,
                troco,
                caixa_atual[0]
            ))

            venda_id = cursor.fetchone()[0]

            for item in carrinho:
                cursor.execute("""
                    INSERT INTO dbo.itens_venda (
                        venda_id,
                        produto_id,
                        quantidade,
                        preco_unitario,
                        subtotal
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    venda_id,
                    item["id"],
                    item["quantidade"],
                    dinheiro(item["preco"]),
                    dinheiro(item["subtotal"])
                ))

                cursor.execute("""
                    UPDATE dbo.produtos
                    SET estoque = estoque - ?
                    WHERE id = ?
                """, (item["quantidade"], item["id"]))

            conexao.commit()

            messagebox.showinfo(
                "Venda",
                f"VENDA REALIZADA!\n\n"
                f"Venda Nº {venda_id}\n"
                f"Total: {moeda(total)}\n"
                f"Pagamento: {forma}"
            )

            carrinho.clear()
            atualizar()
            return venda_id

        except Exception as erro:
            conexao.rollback()
            messagebox.showerror("Erro", str(erro))
            return None

        finally:
            conexao.close()

    def finalizar():
        if not carrinho:
            messagebox.showwarning("Venda", "Carrinho vazio.")
            return

        total = calcular_total()
        pagamento, area_pagamento = criar_tela(
            "Pagamento",
            560,
            650,
            parent=tela
        )

        header_pagamento = tk.Frame(
            area_pagamento,
            bg=COR_CABECALHO,
            padx=24,
            pady=22
        )
        header_pagamento.pack(fill="x")

        tk.Label(
            header_pagamento,
            text="FINALIZAR VENDA",
            font=(FONTE, 19, "bold"),
            bg=COR_CABECALHO,
            fg="#FFFFFF"
        ).pack(anchor="w")
        tk.Label(
            header_pagamento,
            text="Escolha a forma de pagamento",
            font=(FONTE, 10),
            bg=COR_CABECALHO,
            fg="#CBD5E1"
        ).pack(anchor="w", pady=(3, 0))

        resumo_pagamento = criar_card(area_pagamento, padx=22, pady=18)
        resumo_pagamento.pack(fill="x", padx=22, pady=22)
        tk.Label(
            resumo_pagamento,
            text="TOTAL A PAGAR",
            font=(FONTE, 9, "bold"),
            bg=COR_CARD,
            fg=COR_TEXTO_SECUNDARIO
        ).pack(anchor="w")
        tk.Label(
            resumo_pagamento,
            text=moeda(total),
            font=(FONTE, 27, "bold"),
            bg=COR_CARD,
            fg=COR_TEXTO
        ).pack(anchor="w", pady=(3, 0))

        def pagamento_dinheiro():
            tela_dinheiro, area_dinheiro = criar_tela(
                "Dinheiro",
                500,
                610,
                parent=pagamento
            )

            topo_dinheiro = tk.Frame(
                area_dinheiro,
                bg=COR_CABECALHO,
                padx=24,
                pady=20
            )
            topo_dinheiro.pack(fill="x")
            tk.Label(
                topo_dinheiro,
                text="PAGAMENTO EM DINHEIRO",
                font=(FONTE, 17, "bold"),
                bg=COR_CABECALHO,
                fg="#FFFFFF"
            ).pack(anchor="w")

            card_dinheiro = criar_card(area_dinheiro, padx=24, pady=22)
            card_dinheiro.pack(fill="x", padx=24, pady=24)

            tk.Label(
                card_dinheiro,
                text="Total",
                font=(FONTE, 10, "bold"),
                bg=COR_CARD,
                fg=COR_TEXTO_SECUNDARIO
            ).pack(anchor="w")
            tk.Label(
                card_dinheiro,
                text=moeda(total),
                font=(FONTE, 25, "bold"),
                bg=COR_CARD,
                fg=COR_TEXTO
            ).pack(anchor="w", pady=(2, 18))

            tk.Label(
                card_dinheiro,
                text="Valor recebido",
                font=(FONTE, 10, "bold"),
                bg=COR_CARD,
                fg=COR_TEXTO
            ).pack(anchor="w")

            entrada = tk.Entry(
                card_dinheiro,
                font=(FONTE, 18),
                justify="left"
            )
            entrada.pack(fill="x", ipady=9, pady=(6, 16))

            titulo_troco = tk.Label(
                card_dinheiro,
                text="TROCO",
                font=(FONTE, 9, "bold"),
                bg=COR_CARD,
                fg=COR_TEXTO_SECUNDARIO
            )
            titulo_troco.pack(anchor="w")

            label_troco = tk.Label(
                card_dinheiro,
                text="R$ 0,00",
                font=(FONTE, 25, "bold"),
                bg=COR_CARD,
                fg=COR_SUCESSO
            )
            label_troco.pack(anchor="w", pady=(2, 14))

            dados = {"recebido": None, "troco": None}

            def calcular():
                try:
                    recebido = converter_valor(entrada.get())
                except Exception:
                    messagebox.showerror("Erro", "Valor inválido.")
                    return False

                if recebido < total:
                    falta = dinheiro(total - recebido)
                    titulo_troco.config(text="FALTA")
                    label_troco.config(text=moeda(falta), fg=COR_PERIGO)
                    dados["recebido"] = None
                    dados["troco"] = None
                    return False

                troco = dinheiro(recebido - total)
                dados["recebido"] = recebido
                dados["troco"] = troco

                titulo_troco.config(text="TROCO")
                label_troco.config(text=moeda(troco), fg=COR_SUCESSO)
                return True

            def confirmar():
                if not calcular():
                    return

                venda_id = registrar(
                    "Dinheiro",
                    dados["recebido"],
                    dados["troco"]
                )

                if venda_id:
                    tela_dinheiro.destroy()
                    pagamento.destroy()

            botoes_dinheiro = tk.Frame(card_dinheiro, bg=COR_CARD)
            botoes_dinheiro.pack(fill="x", pady=(4, 0))
            botao_moderno(
                botoes_dinheiro,
                "CALCULAR TROCO",
                calcular,
                cor="#475569",
                cor_ativa="#334155",
                fonte=(FONTE, 10, "bold"),
                pady=10
            ).pack(side="left", padx=(0, 8))
            botao_moderno(
                botoes_dinheiro,
                "CONFIRMAR VENDA",
                confirmar,
                cor=COR_SUCESSO,
                cor_ativa="#166534",
                fonte=(FONTE, 10, "bold"),
                pady=10
            ).pack(side="left")

            entrada.bind("<Return>", lambda event: calcular())
            entrada.focus()

        def outro(forma):
            resposta = messagebox.askyesno(
                "Pagamento",
                f"Confirmar {forma}?\n\nTotal: {moeda(total)}"
            )

            if resposta:
                venda_id = registrar(forma)
                if venda_id:
                    pagamento.destroy()

        opcoes = tk.Frame(area_pagamento, bg=COR_FUNDO)
        opcoes.pack(fill="x", padx=22, pady=(0, 24))
        opcoes.columnconfigure(0, weight=1)
        opcoes.columnconfigure(1, weight=1)

        botoes_pagamento = [
            ("DINHEIRO", pagamento_dinheiro),
            ("PIX", lambda: outro("PIX")),
            ("DÉBITO", lambda: outro("Débito")),
            ("CRÉDITO", lambda: outro("Crédito")),
        ]
        for i, (texto, comando) in enumerate(botoes_pagamento):
            botao_moderno(
                opcoes,
                texto,
                comando,
                fonte=(FONTE, 11, "bold"),
                pady=14
            ).grid(
                row=i // 2,
                column=i % 2,
                sticky="ew",
                padx=5,
                pady=5
            )

    botao_moderno(
        area_adicionar,
        "ADICIONAR À VENDA",
        adicionar,
        fonte=(FONTE, 11, "bold"),
        pady=13
    ).pack(fill="x")

    botao_moderno(
        area_acoes,
        "REMOVER ITEM",
        remover,
        cor="#475569",
        cor_ativa="#334155",
        fonte=(FONTE, 10, "bold"),
        padx=14,
        pady=10
    ).pack(side="left", padx=(0, 8))

    botao_moderno(
        area_acoes,
        "FINALIZAR VENDA",
        finalizar,
        cor=COR_SUCESSO,
        cor_ativa="#166534",
        fonte=(FONTE, 11, "bold"),
        padx=18,
        pady=11
    ).pack(side="left")

    entrada_codigo.bind("<Return>", lambda event: adicionar())
    entrada_codigo.focus()

# ==========================================================
# INICIALIZAÇÃO
# ==========================================================

try:
    preparar_banco()
except Exception as erro:
    erro_janela = tk.Tk()
    erro_janela.withdraw()

    messagebox.showerror(
        "Erro no SQL Server",
        "Não foi possível iniciar o Sistema da Loja.\n\n"
        "Verifique se o SQL Server está ligado e se o banco "
        "SistemaLoja existe.\n\n"
        f"Detalhes:\n{erro}"
    )

    erro_janela.destroy()
    raise SystemExit


# ==========================================================
# TELA PRINCIPAL
# ==========================================================

janela = tk.Tk()
janela.title("Sistema da Loja")
configurar_tema(janela)

largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()

largura_principal = min(1180, max(920, largura_tela - 100))
altura_principal = min(790, max(650, altura_tela - 120))

janela.geometry(f"{largura_principal}x{altura_principal}")
janela.minsize(900, 620)

conteudo_principal = criar_area_rolavel(janela)

# ---------- Cabeçalho ----------
header = tk.Frame(
    conteudo_principal,
    bg=COR_CABECALHO,
    padx=30,
    pady=22
)
header.pack(fill="x")
header.columnconfigure(0, weight=1)

bloco_titulo = tk.Frame(header, bg=COR_CABECALHO)
bloco_titulo.grid(row=0, column=0, sticky="w")

tk.Label(
    bloco_titulo,
    text="SISTEMA DA LOJA",
    font=(FONTE, 24, "bold"),
    bg=COR_CABECALHO,
    fg="#FFFFFF"
).pack(anchor="w")

tk.Label(
    bloco_titulo,
    text="PDV • Estoque • Vendas • Relatórios",
    font=(FONTE, 10),
    bg=COR_CABECALHO,
    fg="#CBD5E1"
).pack(anchor="w", pady=(4, 0))

label_status_caixa = tk.Label(
    header,
    text="",
    font=(FONTE, 10, "bold"),
    padx=14,
    pady=8,
    bd=0
)
label_status_caixa.grid(row=0, column=1, sticky="e")

# ---------- Navegação superior ----------
nav = tk.Frame(conteudo_principal, bg="#172033", padx=22, pady=0)
nav.pack(fill="x")

links = [
    ("NOVA VENDA", abrir_venda),
    ("PRODUTOS / ESTOQUE", abrir_produtos),
    ("HISTÓRICO", abrir_historico),
    ("RELATÓRIOS", abrir_relatorios),
]

for texto_link, comando_link in links:
    tk.Button(
        nav,
        text=texto_link,
        command=comando_link,
        bg="#172033",
        fg="#E2E8F0",
        activebackground="#25324A",
        activeforeground="#FFFFFF",
        relief="flat",
        bd=0,
        highlightthickness=0,
        cursor="hand2",
        font=(FONTE, 10, "bold"),
        padx=18,
        pady=13
    ).pack(side="left")

# ---------- Conteúdo ----------
body = tk.Frame(conteudo_principal, bg=COR_FUNDO, padx=28, pady=26)
body.pack(fill="both", expand=True)
body.columnconfigure(0, weight=1)

linha_titulo = tk.Frame(body, bg=COR_FUNDO)
linha_titulo.grid(row=0, column=0, sticky="ew", pady=(0, 18))
linha_titulo.columnconfigure(0, weight=1)

tk.Label(
    linha_titulo,
    text="Painel da loja",
    font=(FONTE, 21, "bold"),
    bg=COR_FUNDO,
    fg=COR_TEXTO
).grid(row=0, column=0, sticky="w")

tk.Label(
    linha_titulo,
    text="Banco: SQL Server • SistemaLoja",
    font=(FONTE, 9),
    bg=COR_FUNDO,
    fg=COR_TEXTO_SECUNDARIO
).grid(row=1, column=0, sticky="w", pady=(3, 0))

# Ação principal
card_venda = criar_card(body, padx=24, pady=22)
card_venda.grid(row=1, column=0, sticky="ew", pady=(0, 18))
card_venda.columnconfigure(0, weight=1)

tk.Label(
    card_venda,
    text="Venda no balcão",
    font=(FONTE, 17, "bold"),
    bg=COR_CARD,
    fg=COR_TEXTO
).grid(row=0, column=0, sticky="w")

tk.Label(
    card_venda,
    text="Abra uma nova venda, leia os produtos e finalize o pagamento.",
    font=(FONTE, 10),
    bg=COR_CARD,
    fg=COR_TEXTO_SECUNDARIO
).grid(row=1, column=0, sticky="w", pady=(4, 0))

botao_moderno(
    card_venda,
    "INICIAR NOVA VENDA",
    abrir_venda,
    cor=COR_SUCESSO,
    cor_ativa="#166534",
    fonte=(FONTE, 11, "bold"),
    padx=20,
    pady=12
).grid(row=0, column=1, rowspan=2, sticky="e", padx=(20, 0))

# Cards de acesso rápido
atalhos = tk.Frame(body, bg=COR_FUNDO)
atalhos.grid(row=2, column=0, sticky="nsew")
for coluna in range(3):
    atalhos.columnconfigure(coluna, weight=1, uniform="atalho")

cards = [
    ("Verificar preço", "Consulte rapidamente preço e estoque pelo código de barras.", abrir_verificar_preco, COR_PRIMARIA),
    ("Produtos / Estoque", "Cadastre, edite e acompanhe os produtos disponíveis.", abrir_produtos, "#475569"),
    ("Histórico de vendas", "Consulte vendas concluídas, detalhes e cancelamentos.", abrir_historico, "#475569"),
    ("Relatórios", "Veja vendas do dia, faturamento e produtos mais vendidos.", abrir_relatorios, "#475569"),
    ("Abrir caixa", "Informe o fundo inicial e comece a operação do caixa.", abrir_caixa, COR_SUCESSO),
    ("Fechar caixa", "Confira os valores e encerre o caixa ao final do turno.", fechar_caixa, COR_PERIGO),
]

for indice, (titulo_card, descricao_card, comando_card, cor_botao) in enumerate(cards):
    linha = indice // 3
    coluna = indice % 3

    card = criar_card(atalhos, padx=20, pady=18)
    card.grid(
        row=linha,
        column=coluna,
        sticky="nsew",
        padx=(0 if coluna == 0 else 7, 0 if coluna == 2 else 7),
        pady=(0 if linha == 0 else 7, 7 if linha == 0 else 0)
    )
    card.columnconfigure(0, weight=1)

    tk.Label(
        card,
        text=titulo_card,
        font=(FONTE, 13, "bold"),
        bg=COR_CARD,
        fg=COR_TEXTO
    ).grid(row=0, column=0, sticky="w")

    tk.Label(
        card,
        text=descricao_card,
        font=(FONTE, 9),
        bg=COR_CARD,
        fg=COR_TEXTO_SECUNDARIO,
        justify="left",
        wraplength=280
    ).grid(row=1, column=0, sticky="nw", pady=(5, 14))

    cor_ativa = (
        COR_PERIGO_HOVER if cor_botao == COR_PERIGO
        else "#166534" if cor_botao == COR_SUCESSO
        else COR_PRIMARIA_HOVER if cor_botao == COR_PRIMARIA
        else "#334155"
    )

    botao_moderno(
        card,
        "ABRIR",
        comando_card,
        cor=cor_botao,
        cor_ativa=cor_ativa,
        fonte=(FONTE, 9, "bold"),
        padx=14,
        pady=8
    ).grid(row=2, column=0, sticky="w")

atualizar_status_caixa()
janela.mainloop()

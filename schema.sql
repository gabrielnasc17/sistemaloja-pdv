-- SistemaLoja - estrutura principal
-- SQL Server

IF DB_ID('SistemaLoja') IS NULL
BEGIN
    CREATE DATABASE SistemaLoja;
END;
GO

USE SistemaLoja;
GO

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
END;
GO

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
END;
GO

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
END;
GO

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
END;
GO

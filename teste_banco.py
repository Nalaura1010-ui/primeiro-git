import sqlite3

# 1. Conecta ao banco (se o arquivo meubanco.db não existir, ele é criado na hora)
conexao = sqlite3.connect("meubanco.db")
cursor = conexao.cursor()

# Cria uma tabela para o teste
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        status TEXT NOT NULL
    )
""")
cursor.execute("""
    INSERT INTO usuarios (nome, status)
    VALUES
        ('Ana', 'ativo'),
        ('João', 'inativo'),
        ('Maria', 'ativo');


"""

)
print("Usuários adicionados com sucesso!")
conexao.commit()
conexao.close()

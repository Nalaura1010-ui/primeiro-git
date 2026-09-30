import sqlite3

conexao= sqlite3.connect("meubanco.db")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cursos TEXT NOT NULL,
        status BOOLEAN NOT NULL
    )
""")
cursor.execute("""
    INSERT INTO cursos (cursos, status)
    VALUES
        ('Eng civil', 'true'),
        ('Eng de minas', 'true'),
        ('Eng de produção', 'true'),
        ('Eng controle e aut', 'true');

""")

conexao.commit()
conexao.close()
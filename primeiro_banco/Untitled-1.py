import sqlite3

conexao= sqlite3.connect("meubanco.db")
cursor = conexao.cursor()

cursor.execute("""
    DROP TABLE tabela_relacionada;
    """)
conexao.commit()
conexao.close()
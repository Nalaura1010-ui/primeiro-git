import sqlite3

conexao = sqlite3.connect("meubanco.db")
cursor = conexao.cursor()

cursor.execute("""
    UPDATE usuarios
    SET status = 'inativo'
""")

conexao.commit()
conexao.close()

print("Todos os usuários foram definidos como inativos.")
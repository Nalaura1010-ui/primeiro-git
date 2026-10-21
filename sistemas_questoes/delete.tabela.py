import sqlite3
import os

pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_banco = os.path.join(pasta_atual, 'sistema_questoes.db')

# 2. Conecta ao banco de dados
conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()


cursor.execute("""
DROP TABLE registro;
""")
print("Tabela apagada com sucesso!")
conexao.commit()
conexao.close()
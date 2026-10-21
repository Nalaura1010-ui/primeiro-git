import sqlite3
import os

# 1. Configura o caminho e conecta ao banco de dados
pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_banco = os.path.join(pasta_atual, 'sistema_questoes.db')

conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()

# 2. Cria a tabela 'registro' se ela ainda não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS registro(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        questao1_id INTEGER NOT NULL,
        questao2_id INTEGER NOT NULL,
        questao3_id INTEGER NOT NULL,
        questao1_enunciado TEXT NOT NULL,
        questao2_enunciado TEXT NOT NULL,
        questao3_enunciado TEXT NOT NULL,
        resultado1 INTEGER NOT NULL CHECK (resultado1 IN (0, 1)),
        resultado2 INTEGER NOT NULL CHECK (resultado2 IN (0, 1)),
        resultado3 INTEGER NOT NULL CHECK (resultado3 IN (0, 1))
    )
""")
print("Tabela 'registro' verificada/criada com sucesso.")

# 3. Busca TODAS as respostas do banco unindo com a tabela 'questoes'
cursor.execute("""
    SELECT 
        r.usuario_id,
        r.questao_id,
        q.enunciado,
        r.resultado
    FROM resposta r
    JOIN questoes q ON r.questao_id = q.id
    ORDER BY r.usuario_id, r.id ASC;
""")

todas_as_respostas = cursor.fetchall()

# Dicionário auxiliar para separar as respostas por aluno
respostas_por_usuario = {}

for linha in todas_as_respostas:
    usuario_id = linha[0]
    if usuario_id not in respostas_por_usuario:
        respostas_por_usuario[usuario_id] = []
    respostas_por_usuario[usuario_id].append(linha)

# Contador para sabermos quantas tentativas NOVAS foram salvas de fato
novos_registros_salvos = 0

# 4. Processa os dados de cada aluno separadamente
for usuario_id, lista_respostas in respostas_por_usuario.items():
    
    # Pula de 3 em 3 para pegar cada tentativa completa
    for i in range(0, len(lista_respostas), 3):
        bloco = lista_respostas[i:i+3]
        
        # Garante que o bloco está completo (tem 3 respostas)
        if len(bloco) == 3:
            q1_id, q1_enun, q1_res = bloco[0][1], bloco[0][2], bloco[0][3]
            q2_id, q2_enun, q2_res = bloco[1][1], bloco[1][2], bloco[1][3]
            q3_id, q3_enun, q3_res = bloco[2][1], bloco[2][2], bloco[2][3]
            
            # --- VERIFICAÇÃO ANTI-DUPLICAÇÃO ---
            # Perguntamos ao banco: "Já existe uma linha no registro com este usuário e essas mesmas 3 questões?"
            cursor.execute("""
                SELECT COUNT(*) FROM registro
                WHERE usuario_id = ? 
                  AND questao1_id = ? 
                  AND questao2_id = ? 
                  AND questao3_id = ?
            """, (usuario_id, q1_id, q2_id, q3_id))
            
            # O fetchone()[0] traz o número de vezes que isso foi encontrado (0 ou 1 ou mais)
            quantidade_existente = cursor.fetchone()[0]
            
            # Se a quantidade for 0, significa que ainda NÃO foi salvo. Podemos inserir!
            if quantidade_existente == 0:
                cursor.execute("""
                    INSERT INTO registro (
                        usuario_id, 
                        questao1_id, questao2_id, questao3_id, 
                        questao1_enunciado, questao2_enunciado, questao3_enunciado, 
                        resultado1, resultado2, resultado3
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    usuario_id, 
                    q1_id, q2_id, q3_id, 
                    q1_enun, q2_enun, q3_enun, 
                    q1_res, q2_res, q3_res
                ))
                novos_registros_salvos += 1
            # Se quantidade_existente for maior que 0, o código simplesmente pula e não faz nada, evitando duplicar.

# 5. Salva as alterações e fecha a conexão
conexao.commit()
print(f"\nProcesso concluído! {novos_registros_salvos} novo(s) registro(s) consolidado(s) adicionado(s) com sucesso.")
conexao.close()
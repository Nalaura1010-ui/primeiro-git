import sqlite3
import os

pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_banco = os.path.join(pasta_atual, 'sistema_questoes.db')

# 2. Conecta ao banco de dados
conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()


cursor.execute("""
SELECT id, nome, email, esporte_interesse_id
FROM usuarios;
""")


linhas= cursor.fetchall()

for id, nome, email, esporte_interesse_id in linhas:
    print(f"{id} - {nome}  - {email} - Esporte de interesse: {esporte_interesse_id}")

# 1. Pede o ID no terminal
id_escolhido = input("\nQual o seu id? ")

# 2. Busca o usuário no banco (trazendo exatamente 3 colunas)
cursor.execute("""
    SELECT id, nome, esporte_interesse_id
    FROM usuarios       
    WHERE id = ?;
""", (id_escolhido,))

usuario = cursor.fetchone()

# 3. Verifica se encontrou o usuário
if usuario is None:
    print("\n[ERRO] Usuário não encontrado no banco de dados!")
else:
    # Acessa os dados diretamente pelos índices da lista/tupla retornada:
    # usuario[0] -> id
    # usuario[1] -> nome
    # usuario[2] -> esporte_interesse_id
    
    esporte_interesse_id = usuario[2]

    print(f"\nUsuário selecionado: {usuario[1]} (Interesse no Esporte ID: {esporte_interesse_id})")

    # 4. Consulta SQL para sortear 1 questão Fácil (1), 1 Média (2) e 1 Difícil (3) do esporte do usuário
    sql_questoes_usuario = """
    WITH questoes_sorteadas AS (
        SELECT 
            id AS questao_id,
            esporte_id,
            enunciado,
            nivel_dificuldade,
            ROW_NUMBER() OVER (
                PARTITION BY nivel_dificuldade 
                ORDER BY RANDOM()
            ) AS posicao_sorteio
        FROM questoes
        WHERE esporte_id = ?
    )
    SELECT 
        questao_id,
        nivel_dificuldade,
        enunciado
    FROM questoes_sorteadas
    WHERE posicao_sorteio = 1
    ORDER BY nivel_dificuldade ASC;
    """

    cursor.execute(sql_questoes_usuario, (esporte_interesse_id,))
    questoes = cursor.fetchall()

    # 5. Imprime o nome do usuário usando usuario[1] sem correr risco de NameError
    print(f"\n=== QUESTÕES SELECIONADAS PARA {str(usuario[1]).upper()} ===")
    
    if not questoes:
        print("Nenhuma questão encontrada para este esporte de interesse.")
    else:
        rotulos_dificuldade = {1: "Fácil (1)", 2: "Média (2)", 3: "Difícil (3)"}
        
        for q_id, nivel, enunciado in questoes:
            nivel_texto = rotulos_dificuldade.get(nivel, str(nivel))
            print(f"\n[ID Questão: {q_id}] - Nível: {nivel_texto}")
            print(f"Enunciado: {enunciado}")
# 5. Cria a tabela de resposta se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resposta(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            resultado BOOLEAN NOT NULL,
            usuario_id INTEGER NOT NULL,
            questao_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)

    rotulos_dificuldade = {1: "Fácil (1)", 2: "Média (2)", 3: "Difícil (3)"}
    
    # Exemplo de loop organizado para tratar a escolha e validação
    sobra = 3  # Número de questões a serem respondidas
    confere=3
    respondida1 = False
    respondida2 = False
    respondida3 = False

    while sobra > 0:
        print("\n=== QUESTÕES DISPONÍVEIS ===")
        for i, (q_id, nivel, enunciado) in enumerate(questoes):
            if respondida1 == False and nivel == 1:
                print(f"\n[id Questão: {q_id}] - Nível: {rotulos_dificuldade.get(nivel, str(nivel))}")
            elif respondida2 == False and nivel == 2:
                print(f"\n[ID Questão: {q_id}] - Nível: {rotulos_dificuldade.get(nivel, str(nivel))}")
            elif respondida3 == False and nivel == 3:
                print(f"\n[ID Questão: {q_id}] - Nível: {rotulos_dificuldade.get(nivel, str(nivel))}")

        escolhida = input(f"\nDigite o Nível da questão que deseja responder: ")
        for q_id, nivel, enunciado in questoes:
        # Estrutura condicional limpa e correta
            if int(escolhida) == 1 and nivel == 1 and respondida1 == False:
                resultado = input(f"Digite o resultado da questão {q_id} (1 para acerto, 0 para erro): ")
                while resultado not in ['0', '1']:
                    resultado = input("Resultado inválido. Por favor, digite 1 para acerto ou 0 para erro: ")
                sobra -= 1
                respondida1 = True
                cursor.execute("""
                    INSERT INTO resposta (nome, resultado, usuario_id, questao_id)
                    VALUES (?, ?, ?, ?);
                """, (usuario[1], int(resultado), usuario[0], q_id))


            elif int(escolhida) == 2 and nivel == 2 and respondida2 == False:
                resultado = input(f"Digite o resultado da questão {q_id} (1 para acerto, 0 para erro): ")
                while resultado not in ['0', '1']:
                    resultado = input("Resultado inválido. Por favor, digite 1 para acerto ou 0 para erro: ")
                sobra -= 1
                respondida2 = True
                cursor.execute("""
                    INSERT INTO resposta (nome, resultado, usuario_id, questao_id)
                    VALUES (?, ?, ?, ?);
                """, (usuario[1], int(resultado), usuario[0], q_id))

            elif int(escolhida) == 3 and nivel == 3 and respondida3 == False:
                resultado = input(f"Digite o resultado da questão {q_id} (1 para acerto, 0 para erro): ")
                while resultado not in ['0', '1']:
                    resultado = input("Resultado inválido. Por favor, digite 1 para acerto ou 0 para erro: ")
                sobra -= 1
                respondida3 = True
                cursor.execute("""
                    INSERT INTO resposta (nome, resultado, usuario_id, questao_id)
                    VALUES (?, ?, ?, ?);
                """, (usuario[1], int(resultado), usuario[0], q_id))

        
            # Insere a resposta diretamente usando os dados que já temos em memória
 
        if confere == sobra:
            print("\n[ERRO] essa questão não corresponde ao nível da questão sorteada. Por favor, escolha novamente.")
            continue
        else:
            confere = sobra
            print(f"\nQuestão {q_id} respondida com sucesso! Questões restantes: {sobra}")

    # Salva as alterações e fecha a conexão
    conexao.commit()
    print("\nTodas as respostas foram salvas com sucesso!")

conexao.close()

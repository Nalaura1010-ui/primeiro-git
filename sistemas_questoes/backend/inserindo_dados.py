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

vet_registro = []

# 1. Pede o ID no terminal
id_escolhido = input("\nQual o seu id? ")

# 2. Busca o usuário no banco (trazendo exatamente 3 colunas)
cursor.execute("""
    SELECT id, nome, esporte_interesse_id
    FROM usuarios       
    WHERE id = ?;
""", (id_escolhido,))

usuario = cursor.fetchone()


if usuario is None:
    print("\n[ERRO] Usuário não encontrado no banco de dados!")
else:
    # Acessa os dados diretamente pelos índices da lista/tupla retornada:
    # usuario[0] -> id
    # usuario[1] -> nome
    # usuario[2] -> esporte_interesse_id
    vet_registro.append(int(id_escolhido))
    vet_registro.append(usuario[1])  # Nome do usuário
    print(f"\nUsuário selecionado: {usuario[1]} (ID: {usuario[0]})")

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
            vet_registro.append(q_id)
        for q_id, nivel, enunciado in questoes:
            vet_registro.append(enunciado)


    # 5. Cria a tabela de registro se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome INTEGER NOT NULL,
            usuario_id INTEGER,
            questao1_id INTEGER,
            questao2_id INTEGER,
            questao3_id INTEGER,
            questao1_enunciado,
            questao2_enunciado,
            questao3_enunciado,
            resultado1 INTEGER NOT NULL CHECK (resultado1 IN (0, 1)),
            resultado2 INTEGER NOT NULL CHECK (resultado2 IN (0, 1)),
            resultado3 INTEGER NOT NULL CHECK (resultado3 IN (0, 1))
        )
    """)
    print("\nTabela 'registro' verificada/criada com sucesso.")

    rotulos_dificuldade = {1: "Fácil (1)", 2: "Média (2)", 3: "Difícil (3)"}
        
        # Exemplo de loop organizado para tratar a escolha e validação
    sobra = 3  # Número de questões a serem respondidas
    confere=3
    respondidas = [False, False, False]


    while sobra > 0:
        print("\n=== QUESTÕES DISPONÍVEIS ===")
        for i, (q_id, nivel, enunciado) in enumerate(questoes):
            if respondidas[i] == False and nivel == 1:
                print(f"\n[id Questão: {q_id}] - Nível: {rotulos_dificuldade.get(nivel, str(nivel))}")
            elif respondidas[i] == False and nivel == 2:
                print(f"\n[ID Questão: {q_id}] - Nível: {rotulos_dificuldade.get(nivel, str(nivel))}")
            elif respondidas[i] == False and nivel == 3:
                print(f"\n[ID Questão: {q_id}] - Nível: {rotulos_dificuldade.get(nivel, str(nivel))}")

        escolhida = input(f"\nDigite o Nível da questão que deseja responder: ")
        for q_id, nivel, enunciado in questoes:
        # Estrutura condicional limpa e correta
            if int(escolhida) == 1 and nivel == 1 and respondidas[0] == False:
                resultado = input(f"Digite o resultado da questão {q_id} (1 para acerto, 0 para erro): ")
                while resultado not in ['0', '1']:
                    resultado = input("Resultado inválido. Por favor, digite 1 para acerto ou 0 para erro: ")
                resposta1= resultado
                sobra -= 1
                respondidas[0] = True
                


            elif int(escolhida) == 2 and nivel == 2 and respondidas[1] == False:
                resultado = input(f"Digite o resultado da questão {q_id} (1 para acerto, 0 para erro): ")
                while resultado not in ['0', '1']:
                    resultado = input("Resultado inválido. Por favor, digite 1 para acerto ou 0 para erro: ")
                sobra -= 1
                respondidas[1] = True
                resposta2 = resultado


            elif int(escolhida) == 3 and nivel == 3 and respondidas[2] == False:
                resultado = input(f"Digite o resultado da questão {q_id} (1 para acerto, 0 para erro): ")
                while resultado not in ['0', '1']:
                    resultado = input("Resultado inválido. Por favor, digite 1 para acerto ou 0 para erro: ")
                sobra -= 1
                respondidas[2] = True
                resposta3 = resultado

        
            # Insere a resposta diretamente usando os dados que já temos em memória

        if confere == sobra:
            print("\n[ERRO] essa questão não corresponde ao nível da questão sorteada. Por favor, escolha novamente.")
            continue
        else:
            confere = sobra
            print(f"\nQuestão {q_id} respondida com sucesso! Questões restantes: {sobra}")

    vet_registro.append(int(resposta1))
    vet_registro.append(int(resposta2))
    vet_registro.append(int(resposta3))

    cursor.execute("""
        INSERT INTO registro (
            usuario_id, 
            nome, 
            questao1_id, questao2_id, questao3_id,
            questao1_enunciado, questao2_enunciado, questao3_enunciado,
            resultado1, resultado2, resultado3
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, vet_registro)

    # Salva as alterações e fecha a conexão
    conexao.commit()
    print("\nTodas as respostas foram salvas com sucesso!")

    conexao.close()

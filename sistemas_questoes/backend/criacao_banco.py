import sqlite3

# Nome do arquivo do banco de dados
DB_NAME = "sistema_questoes.db"

def conectar_banco(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    # Habilita explicitamente o suporte a chaves estrangeiras no SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_tabelas(conn):
    cursor = conn.cursor()
    
    # 1. Tabela de Esportes / Temas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS esportes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT
    );
    """)

    # 2. Tabela de Usuários / Alunos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        esporte_interesse_id INTEGER NOT NULL,
        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (esporte_interesse_id) REFERENCES esportes(id) ON DELETE RESTRICT
    );
    """)

    # 3. Tabela de Questões
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        esporte_id INTEGER NOT NULL,
        enunciado TEXT NOT NULL,
        nivel_dificuldade INTEGER NOT NULL CHECK (nivel_dificuldade BETWEEN 1 AND 3),
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (esporte_id) REFERENCES esportes(id) ON DELETE RESTRICT
    );
    """)

    # 4. Tabela Fato: Histórico de Respostas dos Alunos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS respostas_usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        questao_id INTEGER NOT NULL,
        acertou INTEGER NOT NULL CHECK (acertou IN (0, 1)),
        tempo_resposta_segundos INTEGER,
        data_resposta DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
        FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    print("✓ Tabelas criadas com sucesso!")

def popular_dados_iniciais(conn):
    cursor = conn.cursor()

    # Inserção dos Esportes (Cursos/Temas)
    esportes_data = [
        ("Futebol", "Perguntas sobre regras, fundamentos e táticas de futebol"),
        ("Natação", "Perguntas sobre estilos, regras e hidrodinâmica"),
        ("Vôlei", "Perguntas sobre regras, rodízio e fundamentos do vôlei"),
        ("Handebol", "Perguntas sobre área de gol, regras e passos"),
        ("Basquete", "Perguntas sobre tempo, pontuação e violações no basquete")
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO esportes (nome, descricao) VALUES (?, ?);
    """, esportes_data)

    # Mapear nome do esporte -> id correspondente
    cursor.execute("SELECT nome, id FROM esportes;")
    esporte_map = dict(cursor.fetchall())

    # Lista das 25 Questões
    questoes_raw = [
        # --- Futebol ---
        ("Futebol", "Quantos jogadores de cada equipe começam uma partida de futebol em campo?", 1),
        ("Futebol", "Qual é o nome da infração cometida quando um jogador toca intencionalmente a bola com a mão ou o braço, em situações proibidas pela regra?", 1),
        ("Futebol", "O que acontece quando um jogador recebe dois cartões amarelos na mesma partida?", 2),
        ("Futebol", "Qual é a função do goleiro e em qual área do campo ele pode tocar a bola com as mãos, respeitando as regras?", 2),
        ("Futebol", "O que caracteriza uma posição de impedimento e em que momento ela deve ser avaliada?", 3),

        # --- Natação ---
        ("Natação", "Quais são os quatro estilos oficiais da natação competitiva?", 1),
        ("Natação", "Qual estilo de natação é geralmente considerado o mais rápido?", 1),
        ("Natação", "Qual é a principal diferença entre o nado peito e o nado borboleta em relação aos movimentos dos braços e das pernas?", 2),
        ("Natação", "Em uma piscina olímpica, qual é a distância de uma piscina de uma extremidade à outra?", 2),
        ("Natação", "Por que a posição hidrodinâmica do corpo é importante para reduzir a resistência da água e melhorar o desempenho do nadador?", 3),

        # --- Vôlei ---
        ("Vôlei", "Quantos jogadores de cada equipe ficam em quadra durante uma partida de vôlei?", 1),
        ("Vôlei", "Quantos toques, no máximo, uma equipe pode dar na bola antes de enviá-la para o outro lado da rede, sem contar o toque no bloqueio?", 1),
        ("Vôlei", "O que é um rodízio no vôlei e quando ele acontece?", 2),
        ("Vôlei", "Qual é a função do líbero e quais são algumas das restrições específicas desse jogador?", 2),
        ("Vôlei", "Em uma jogada, um jogador realiza o bloqueio e a bola volta para o próprio time. Quantos toques a equipe ainda pode realizar antes de devolver a bola ao adversário?", 3),

        # --- Handebol ---
        ("Handebol", "Quantos jogadores de cada equipe ficam em quadra, incluindo o goleiro?", 1),
        ("Handebol", "Qual é o principal objetivo de uma partida de handebol?", 1),
        ("Handebol", "Quantos passos um jogador pode dar segurando a bola sem quicá-la?", 2),
        ("Handebol", "Qual é a função do goleiro e quais são as particularidades da área de gol no handebol?", 2),
        ("Handebol", "O que acontece quando um defensor impede uma clara oportunidade de gol cometendo uma infração dentro da área de gol?", 3),

        # --- Basquete ---
        ("Basquete", "Quantos jogadores de cada equipe ficam em quadra durante uma partida de basquete?", 1),
        ("Basquete", "Quantos pontos vale uma cesta convertida de fora da linha de três pontos?", 1),
        ("Basquete", "O que é uma violação de caminhada (andada) no basquete?", 2),
        ("Basquete", "O que é um rebote e qual é sua importância durante uma partida?", 2),
        ("Basquete", "O que é a regra dos 24 segundos e qual é sua finalidade no basquete?", 3)
    ]

    questoes_data = [
        (esporte_map[esporte], enunciado, nivel)
        for esporte, enunciado, nivel in questoes_raw
    ]

    cursor.executemany("""
    INSERT INTO questoes (esporte_id, enunciado, nivel_dificuldade) 
    VALUES (?, ?, ?);
    """, questoes_data)

    # Inserção de Usuários/Alunos Fictícios
    usuarios_data = [
        ("Lucas Silva", "lucas.silva@email.com", esporte_map["Futebol"]),
        ("Mariana Souza", "mariana.souza@email.com", esporte_map["Natação"]),
        ("Beatriz Lima", "beatriz.lima@email.com", esporte_map["Vôlei"]),
        ("Gabriel Alves", "gabriel.alves@email.com", esporte_map["Basquete"]),
        ("Carla Pereira", "carla.pereira@email.com", esporte_map["Handebol"])
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO usuarios (nome, email, esporte_interesse_id)
    VALUES (?, ?, ?);
    """, usuarios_data)

    conn.commit()
    print("✓ Carga de dados inicial realizada com sucesso!")

if __name__ == "__main__":
    conexao = conectar_banco()
    criar_tabelas(conexao)
    popular_dados_iniciais(conexao)
    conexao.close()
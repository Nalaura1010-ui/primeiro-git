import sqlite3

# Banco em memória: some quando o script termina, então dá para
# rodar quantas vezes quiser sem estragar o meubanco.db.
conexao = sqlite3.connect(":memory:")
conexao.execute("PRAGMA foreign_keys = ON")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE,
        status TEXT NOT NULL DEFAULT 'ativo'
            CHECK (status IN ('ativo', 'inativo'))
    )
""")
cursor.execute("""
    CREATE TABLE matriculas (
        id INTEGER PRIMARY KEY,
        usuario_id INTEGER NOT NULL,
        curso TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )
""")
cursor.execute("INSERT INTO usuarios (nome, email) " \
"VALUES ('Ana', 'ana@email.com')")
conexao.commit()


def titulo(texto):
    print("\n" + "=" * 55)
    print(texto)
    print("=" * 55)


# -----------------------------------------------------------
titulo("1. ValueError: texto onde se esperava número")
# Erro do Python, não do banco. Acontece antes do SQL.
# Na aula, troque "abc" por input("Digite o id: ").
try:
    id_escolhido = int("9.9")
except ValueError as erro:
    print("Capturado ValueError ->", erro)
    print("Lição: validar a entrada antes de mandar para o banco.")


# -----------------------------------------------------------
titulo("2. OperationalError: tabela que não existe")
try:
    cursor.execute("SELECT * FROM alunos")
except sqlite3.OperationalError as erro:
    print("Capturado OperationalError ->", erro)


# -----------------------------------------------------------
titulo("3. OperationalError: erro de digitação no SQL")
try:
    cursor.execute("SELEC id, nome FROM usuarios")
except sqlite3.OperationalError as erro:
    print("Capturado OperationalError ->", erro)


# -----------------------------------------------------------
titulo("4. IntegrityError: NOT NULL (nome vazio)")
try:
    cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)",
                   (None, "semnome@email.com"))
except sqlite3.IntegrityError as erro:
    print("Capturado IntegrityError ->", erro)


# -----------------------------------------------------------
titulo("5. IntegrityError: UNIQUE (email repetido)")
try:
    cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)",
                   ("Outra Ana", "ana@email.com"))
except sqlite3.IntegrityError as erro:
    print("Capturado IntegrityError ->", erro)


# -----------------------------------------------------------
titulo("6. IntegrityError: CHECK (status incorreto)")
try:
    cursor.execute("UPDATE usuarios SET status = 'davi' WHERE id = ?", (1,))
except sqlite3.IntegrityError as erro:
    print("Capturado IntegrityError ->", erro)


# -----------------------------------------------------------
titulo("7. IntegrityError: FOREIGN KEY (usuário inexistente)")
try:
    cursor.execute("INSERT INTO matriculas (usuario_id, curso) VALUES (?, ?)",
                   (99, "Eng de produção"))
except sqlite3.IntegrityError as erro:
    print("Capturado IntegrityError ->", erro)
    print("Lição: só funciona com PRAGMA foreign_keys = ON.")


# -----------------------------------------------------------
titulo("8. ProgrammingError: esqueceu a vírgula da tupla")
# ("12") é só um texto entre parênteses, não uma tupla.
# O sqlite3 trata cada caractere como um parâmetro: '1' e '2'.
try:
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", ("1"))
except sqlite3.ProgrammingError as erro:
    print("Capturado ProgrammingError ->", erro)



# -----------------------------------------------------------
titulo("9. NÃO é erro: DELETE de um id que não existe")
# Nenhuma exceção acontece! O except não pega isso.
# Por isso usamos o rowcount.
try:
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (2,))
    print("Nenhuma exceção. rowcount =", cursor.rowcount)
    if cursor.rowcount == 0:
        print("Lição: id inexistente se trata com rowcount, não com except.")
except sqlite3.Error as erro:
    print("Isto não vai ser impresso.", erro)


# -----------------------------------------------------------
titulo("10. ROLLBACK: a 1ª operação dá certo, a 2ª falha")


def contar_usuarios():
    return cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]


print("Usuários antes:", contar_usuarios())
try:
    cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)",
                   ("Bruno", "bruno@email.com"))
    print("Bruno inserido (ainda sem commit). Usuários agora:", contar_usuarios())

    # Esta linha falha: email repetido.
    cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)",
                   ("Carla", "ana@email.com"))

    conexao.commit()  # nunca chega aqui
except sqlite3.IntegrityError as erro:
    print("Erro na 2ª operação ->", erro)
    conexao.rollback()
    print("Rollback feito. Usuários depois:", contar_usuarios())
    print("Lição: o Bruno também foi desfeito. Ou grava tudo, ou nada.")


# -----------------------------------------------------------
titulo("11. Ordem dos except: do mais específico ao mais geral")
# sqlite3.Error é o "pai" de IntegrityError e OperationalError.
# Se ele vier primeiro, os específicos nunca são alcançados.
try:
    cursor.execute("INSERT INTO usuarios (nome) VALUES (NULL)")
except sqlite3.IntegrityError as erro:
    print("Problema nos dados ->", erro)
except sqlite3.OperationalError as erro:
    print("Problema no comando SQL ->", erro)
except sqlite3.Error as erro:
    print("Qualquer outro erro do banco ->", erro)


# -----------------------------------------------------------
titulo("12. finally + ProgrammingError: usar a conexão já fechada")
try:
    cursor.execute("SELECT * FROM usuarios")
finally:
    # O finally roda SEMPRE, com ou sem erro.
    conexao.close()
    print("finally executado: conexão fechada.")

try:
    cursor.execute("SELECT * FROM usuarios")
except sqlite3.ProgrammingError as erro:
    print("Capturado ProgrammingError ->", erro)
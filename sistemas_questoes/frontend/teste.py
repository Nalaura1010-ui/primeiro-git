from PySide6.QtWidgets import QApplication, QLabel

app = QApplication([])
janela = QLabel("Hello World")
janela2 = QLabel("Bem vindo ao Sistema de Questões")
janela.resize(500, 500)
janela.show()
janela2.show()
app.exec()
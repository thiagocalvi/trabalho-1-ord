import sys
from GerenciadorArquivo import GerenciadorArquivo
from Jogo import Jogo

class Programa:
    """Classe principal que gerencia a execução do programa."""

    def __init__(self):
        """Inicializa o programa com um GerenciadorArquivo."""
        self.gerenciador = GerenciadorArquivo('dados.dat')

    def executar(self, modo):
        """Executa o programa no modo especificado."""
        self.gerenciador.abrir()

        if modo == '-e':
            self.processar_arquivo_operacoes(sys.argv[2])
        elif modo == '-p':
            self.gerenciador.imprimir_led()

        self.gerenciador.fechar()

    def processar_arquivo_operacoes(self, nome_arquivo):
        """Processa o arquivo de operações, executando cada operação."""
        with open(nome_arquivo, 'r') as arquivo:
            for linha in arquivo:
                operacao = linha.strip().split(' ', 1)
                if operacao[0] == 'b':
                    self.gerenciador.buscar(int(operacao[1]))
                elif operacao[0] == 'i':
                    dados = operacao[1].split('|')
                    jogo = Jogo(*dados[:-1])  # Ignora o último campo vazio
                    self.gerenciador.inserir(jogo)
                elif operacao[0] == 'r':
                    self.gerenciador.remover(int(operacao[1]))

def main():
    """Função principal que inicia a execução do programa."""
    if len(sys.argv) != 3:
        print("Uso: python programa.py [-e arquivo_operacoes | -p]")
        return

    programa = Programa()
    programa.executar(sys.argv[1])

if __name__ == "__main__":
    main()
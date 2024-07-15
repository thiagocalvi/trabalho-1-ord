#Criar o fluxo de execução do programa aqui
from GerenciadorArquivo import GerenciadorArquivo

def main():
    repositorio = GerenciadorArquivo('Dados.dat')
    repositorio.abrirArquivo()
    repositorio.abrirArquivoOperacoes('operacao.txt')
    operacao,dados = repositorio.lerArquivoOperacoes()
    while operacao != "Fim das operações" and dados != "Acabou":
        if operacao == 'b':
            x = repositorio.buscarRegistro(int(dados))
        elif operacao == 'r':
            x = repositorio.removerRegistro(int(dados))
        elif operacao == 'i':
            x = repositorio.inserirRegistro(dados)
        print(x)
        
        operacao,dados = repositorio.lerArquivoOperacoes()

main()



import sys
import os
from GerenciadorArquivo import GerenciadorArquivo

def main():

    if len(sys.argv) < 2:
        print("Argumentos Insuficientes")
        sys.exit()

    if not os.path.exists("./dados.dat"):
        print("Erro: Arquivo dados.dat não encontrado")
        sys.exit()

    else:
        gerenciador = GerenciadorArquivo('dados.dat')
        gerenciador.abrirArquivo()
        
        if len(sys.argv) == 2 and sys.argv[1] == "-p":
            gerenciador.imprimirLED()
            gerenciador.fecharArquivo()

        elif len(sys.argv) == 3 and sys.argv[1] == "-e":
            gerenciador.abrirArquivoOperacoes(sys.argv[2])
            operacao, dados = gerenciador.lerArquivoOperacoes()
            
            while operacao != "Fim das operações" and dados != "Acabou":
                
                identificador = int(dados[1].split("|")[0])
                match (operacao):
                    
                    case 'b':
                        print(f"Busca pelo registro de chave \"{identificador}\"")
                        retornoFuncao = gerenciador.buscarRegistro(identificador)
                        if retornoFuncao[1] == 0: 
                            print(retornoFuncao[0])
                        else:
                            print(f"{retornoFuncao[1]} ({retornoFuncao[3]} bytes)")
                            print(f"Local: offset = {retornoFuncao[2]} bytes ({hex(retornoFuncao[2])})\n")


                    case 'i':
                        gerenciador.inserirRegistro(dados[1])

                    case 'r':
                        gerenciador.removerRegistro(identificador)

                operacao, dados = gerenciador.lerArquivoOperacoes()
            
            gerenciador.fecharArquivoOperacoes()
            gerenciador.fecharArquivo()

if __name__ == '__main__':
    main()
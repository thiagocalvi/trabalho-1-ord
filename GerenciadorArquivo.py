import Jogo

class GerenciadorArquivo:
    def __init__(self, path_file:str, operations_file:str, header_size=4, record_size_field=2, min_size_fragmentation=10) -> None:
        self.file = path_file
        self.operations_file = operations_file
        self.HEADER_SIZE = header_size
        self.MIN_SIZE_FRAGMENTATION = min_size_fragmentation
        self.RECORD_SIZE_FIELD = record_size_field

    def abirArquivo(self) -> None:
        try:
            self.file = open(self.file, 'r+b')
            self.operations_file = open(self.operations_file, 'r')
        except:
            raise FileNotFoundError
        
    def fecharArquivo(self) -> None:
        self.file.close()
        self.operations_file.close()
    
    def tamanhoRegistro(self, byteOffset) -> int:
        self.file.seek(byteOffset)
        tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
        return tam_registro
    
    def resetPonteiro(self) -> None:
        self.file.seek(0)

    def lerCabecalho(self) -> int:
        self.resetPonteiro()
        cabecalho = int.from_bytes(self.file.read(self.HEADER_SIZE))
        return cabecalho

    def escreverCabecalho(self, offset:int) -> None:
        offset = offset.to_bytes(self.HEADER_SIZE)    
        self.resetPonteiro()
        self.file.write(offset)

    def buscarRegistro(self, indenficador:str):
        
        offset = self.HEADER_SIZE
        
        self.file.seek(offset)

        tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))

        while tam_registro > 0:
            
            if self.file.read(1).decode() != "*":
                self.file.seek(-1, 1)
                registro = self.file.read(tam_registro).decode()
                registro = registro.split("|")

                if indenficador in registro:
                    return [registro[:-1], offset, tam_registro]
            
                tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
                offset += tam_registro + self.RECORD_SIZE_FIELD
            
            self.file.seek(-1, 1)
            tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            offset += tam_registro + self.RECORD_SIZE_FIELD
        
        return "Registro não encontrado"

    def inserirRegistro(self, dados_registro:str):
        
        buffer = dados_registro.encode()
        tam_registro = len(buffer) + self.RECORD_SIZE_FIELD
        offset_registro_LED = self.lerCabecalho()
        tam_registro_LED = self.tamanhoRegistro(offset_registro_LED)

        if tam_registro == tam_registro_LED:
            self.file.seek(offset_registro_LED+self.RECORD_SIZE_FIELD)
            self.file.write(buffer)
        
        elif tam_registro < tam_registro_LED:

            self.file.seek(offset_registro_LED)
            self.file.write(tam_registro.to_bytes(self.RECORD_SIZE_FIELD))
            
            offset_fragmentacao = offset_registro_LED + tam_registro + self.RECORD_SIZE_FIELD
            tam_fragmentacao = tam_registro_LED - (tam_registro - self.RECORD_SIZE_FIELD)

            self.file.write(buffer)
            
            if tam_fragmentacao >= self.MIN_SIZE_FRAGMENTATION:
                self.file.seek(offset_fragmentacao)
                n_buffer = n_buffer.ljust(tam_fragmentacao - self.RECORD_SIZE_FIELD, b'\0')
                self.file.write(tam_fragmentacao.to_bytes(self.RECORD_SIZE_FIELD))
                self.file.write(n_buffer)
                self.inserirEspacoLED(offset_fragmentacao, tam_fragmentacao)

        else:
            self.file.seek(0, 2)
            self.file.write(tam_registro.to_bytes(self.HEADER_SIZE))
            self.file.write(buffer)

    def removerRegistro(self, identificador):
        offset, tam_registro = self.buscarRegistro(identificador)[-2:]
        self.file.seek(offset+self.RECORD_SIZE_FIELD)
        char_remocao = "*".encode()
        self.file.write(char_remocao)
        self.inserirEspacoLED(offset, tam_registro)


    def percorrerArquivo(self):
        self.file.seek(self.HEADER_SIZE)
        
        bytesOffsets = []
        bytesOffsets.append(self.file.tell())
        tam = int.from_bytes(self.file.read(2))
        c = self.file.read(tam).decode()

        while c != "":
            print(c.split("|"))
            bytesOffsets.append(self.file.tell())
            tam = int.from_bytes(self.file.read(2))
            c = self.file.read(tam).decode()
        
        print(bytesOffsets)


    #Manipulação do arquivo de operações
    def lerArquivoOperacoes(self):
            
        line = self.operations_file.readline()
        
        if line != "":
            opracao = line[0]
            dados = line[1:]

            return opracao, dados
        
        return "Fim das operações"


    #GerenciadorLED
    def inserirEspacoLED(self, offset_novo_espaco:int, tam_novo_espaco:int) -> None:

        cabecalho = int.from_bytes(self.lerCabecalho())
        
        if cabecalho == -1:
            self.file.seek(offset_novo_espaco+3)
            self.file.write(cabecalho.to_bytes(self.HEADER_SIZE))
            self.escreverCabecalho(offset_novo_espaco)
        else:
            index = cabecalho
            self.file.seek(index)
            tam_espaco_atual = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
        
            if tam_novo_espaco >= tam_espaco_atual:
                self.file.seek(offset_novo_espaco+3)
                self.file.write(index.to_bytes(self.HEADER_SIZE))
                self.escreverCabecalho(offset_novo_espaco.to_bytes(self.HEADER_SIZE))
            
            else:
                while index != -1:  
                    self.file.seek(index)
                    tam_espaco_atual = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
                    self.file.seek(1, 1)
                    proximo_offset = int.from_bytes(self.file.read(self.HEADER_SIZE))
                    if tam_novo_espaco >= tam_espaco_atual:
                        self.file.seek(offset_novo_espaco)
                        self.file.seek(3, 1)
                        self.file.write(proximo_offset.to_bytes(self.HEADER_SIZE))
                        
                        self.file.seek(index)
                        self.file.seek(3, 1)
                        self.file.write(offset_novo_espaco.to_bytes(self.HEADER_SIZE))
                        break
                    elif proximo_offset == -1:
                        self.file.seek(index)
                        self.file.seek(3, 1)
                        self.file.write(offset_novo_espaco.to_bytes(self.HEADER_SIZE))
                                                    
                        self.file.seek(offset_novo_espaco)
                        self.file.seek(3, 1)
                        end_led = -1
                        self.file.write(end_led.to_bytes(self.HEADER_SIZE))
                        break
                    
                    index:int = proximo_offset


    def removerEspacoLED(self) -> None:

        cabeca_led:int = self.lerCabecalho()

        if cabeca_led != -1:
            self.file.seek(cabeca_led)
            self.seek(3, 1)
            nova_cabeca:bytes = self.file.read(self.HEADER_SIZE)
            self.escreverCabecalho(nova_cabeca)

            return "Espaço removido!"
        
        else:
            return "A LED está vazia!"

    def imprimirLED(self) -> None:
        # LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
        #Total: 3 espacos disponiveis
        
        lista:list[list] = []
        offset:int = self.lerCabecalho()
        
        while offset != -1:
            self.file.seek(offset)
            tam = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            lista.append([offset, tam])
            self.file.seek(1)
            offset:int = int.from_bytes(self.file.read(self.HEADER_SIZE))
            
       
        lista.append([f"offset: {offset}"])
        
        for x in lista:
            if x[1] != -1:
                print(f"[offset: {x[0]}, tam: {x[1]}] -> ")
            else:
                print(f"[offset: {x[0]}]")

        print(f"\n Total: {self.tamanhoLED()} de espaços disponiveis")

    def tamanhoLED(self) -> int:
        tam_LED:int = 0
        offset:int = self.lerCabecalho()

        while offset != -1:
            self.file.seek(offset+3)
            offset:int = int.from_bytes(self.file.read(self.HEADER_SIZE))
            tam_LED += 1

        return tam_LED




a = GerenciadorArquivo("dados.dat", "operacao.txt")
a.abirArquivo()
#print(a.lerCabecalho())
#a.escreverCabecalho(55)
#a.percorrerArquivo()
#print(a.tamanhoEspaco(4))
#print(a.buscarRegistro("100"))
print(a.lerArquivoOperacoes())
print(a.lerArquivoOperacoes())
print(a.lerArquivoOperacoes())
print(a.lerArquivoOperacoes())
print(a.lerArquivoOperacoes())
print(a.lerArquivoOperacoes())
print(a.lerArquivoOperacoes())


a.fecharArquivo()
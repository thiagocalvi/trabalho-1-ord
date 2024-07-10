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
        if type(offset) != bytes:
            offset = offset.to_bytes(self.HEADER_SIZE)

        self.resetPonteiro()
        self.file.write(offset)

    def buscarRegistro(self, indenficador:int):
        
        offset = self.HEADER_SIZE
        
        self.file.seek(offset)

        tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))

        while tam_registro > 0:
                    
            if self.file.read(1).decode() != "*":
                self.file.seek(-1, 1)
                registro = self.file.read(tam_registro).decode()
                registro = registro.split("|")[:-1]
    
                if indenficador == int(registro[0]):
                    return [registro[:-1], int(offset), int(tam_registro)]
    
                offset += tam_registro + self.RECORD_SIZE_FIELD
                tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            
            else:
                
                offset += tam_registro + self.RECORD_SIZE_FIELD
                self.file.seek(offset)
                tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
        
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


    #somente para teste
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
            dados = line[1:].strip()

            return opracao, dados
        
        return "Fim das operações"


    #GerenciadorLED
    #ainda não está funcionando corretemente
    def inserirEspacoLED(self, offset_novo_espaco:int, tam_novo_espaco:int) -> None:
        offset_LED = self.lerCabecalho()

        if offset_LED == -1:
            self.file.seek(offset_novo_espaco+3)
            self.file.write(offset_LED.to_bytes(self.HEADER_SIZE))
            self.escreverCabecalho(offset_novo_espaco)

        else:
            while offset_LED != -1:
                self.file.seek(offset_LED)
                tam_atual = int.from_bytes(self.file.write(self.RECORD_SIZE_FIELD))
                self.file.seek(1,1)
                next_offset = int.from_bytes(self.file.write(self.HEADER_SIZE))

                if tam_novo_espaco >= tam_atual and next_offset == -1:
                    self.file.seek(offset_novo_espaco+3)
                    self.file.write(offset_LED.to_bytes(self.HEADER_SIZE))
                    self.escreverCabecalho(offset_novo_espaco)
                    break

                self.file.seek(next_offset)
                tam_next_offset = int.from_bytes(self.file.seek(self.HEADER_SIZE))

                if tam_novo_espaco >= tam_next_offset:
                    self.file.seek(offset_novo_espaco+3)
                    self.file.write(next_offset.to_bytes(self.HEADER_SIZE))
                    self.file.seek(offset_LED)
                    self.file.write(offset_novo_espaco.to_bytes(self.HEADER_SIZE))
                    break
    
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
        # Total: 3 espaços disponíveis
        
        lista: list[list[int]] = []
        offset: int = self.lerCabecalho()
        
        if offset == -1:
            return "LED vazia"
        
        while offset != -1:
            print(offset)
            self.file.seek(offset)
            tam = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            lista.append([offset, tam])
            next_offset = self.file.read(self.HEADER_SIZE)
            offset = int.from_bytes(next_offset, signed=True)
        
        # Imprimir a lista de offsets e tamanhos
        for x in lista:
            print(f"[offset: {x[0]}, tam: {x[1]}] -> ", end="")
        
        print("[offset: -1]")
        print(f"\nTotal: {self.tamanhoLED()} espaços disponíveis")

    def tamanhoLED(self) -> int:
        tam_LED:int = 0
        offset:int = self.lerCabecalho()

        while offset != -1:
            self.file.seek(offset+3)
            offset:int = int.from_bytes(self.file.read(self.HEADER_SIZE))
            tam_LED += 1

        return tam_LED







a = GerenciadorArquivo("3.dat", "operacao.txt")
a.abirArquivo()
# print(a.lerArquivoOperacoes())
# print(a.lerArquivoOperacoes())

#print(a.buscarRegistro(1))
#print(a.buscarRegistro(2))
#print(a.buscarRegistro(3))

a.removerRegistro(1)

a.removerRegistro(2)

a.removerRegistro(3)

# a.initCabecalho()
# a.imprimirLED()
a.fecharArquivo()
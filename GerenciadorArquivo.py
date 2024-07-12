import struct

class GerenciadorArquivo:
    def __init__(self, path_file:str, header_size=4, record_size_field=2, min_size_fragmentation=10) -> None:
        self.file = path_file
        self.operations_file = None
        self.HEADER_SIZE = header_size
        self.MIN_SIZE_FRAGMENTATION = min_size_fragmentation
        self.RECORD_SIZE_FIELD = record_size_field


    def abirArquivo(self) -> None:
        try:
            self.file = open(self.file, 'r+b')
        except:
            raise FileNotFoundError

    def abrirArquivoOperacoes(self, operations_file:str) -> None:
        try:
            self.operations_file = open(operations_file, 'r')
        except:
            raise FileNotFoundError

    def fecharArquivo(self) -> None:
        self.file.close()
    
    def fecharArquivoOperacoes(self) -> None:
        self.operations_file.close()

    #Finalizado e testado
    def tamanhoRegistro(self, offset) -> int:
        self.file.seek(offset)
        tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
        return tam_registro
    
    '''
    #Pode ser não utilizado
    def resetPonteiro(self) -> None:
        self.file.seek(0)

    #Pode ser não utilizado
    def lerCabecalho(self) -> int:
        self.resetPonteiro()
        return struct.unpack("I", self.file.read(self.HEADER_SIZE))[0]
    
    #Pode ser não utilizado
    def escreverCabecalho(self, offset:int) -> None:
        self.resetPonteiro()
        self.file.write(struct.pack('I', offset))
    '''
    
    #Finalizado e testado
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


    #Finalizado e não testado, na teoria é para funcionar
    def inserirRegistro(self, dados_registro:str):
        
        n_buffer = b''
        buffer = dados_registro.encode()
        tam_registro = len(buffer)
        self.file.seek(0)

        offset_registro_LED = self.file.read(self.HEADER_SIZE)

        if offset_registro_LED == b'\xff\xff\xff\xff':
            #Inserir registro no final do arquivo
            self.file.seek(0, 2)
            self.file.write(tam_registro.to_bytes(self.RECORD_SIZE_FIELD))
            self.file.write(buffer)
            return "Registro enserido no final do arquivo"


        offset_registro_LED = struct.unpack("I", offset_registro_LED)[0]
        tam_registro_LED = self.tamanhoRegistro(offset_registro_LED)

        if tam_registro == tam_registro_LED:
            #Inserir o registro no primeiro espaço disponivel na led, 
            #os dois registros tem mesmo tamanho
            
            #remover espaço da LED
            self.removerEspacoLED()

            self.file.seek(offset_registro_LED+self.RECORD_SIZE_FIELD)
            self.file.write(buffer)
            
        
        elif tam_registro < tam_registro_LED:
            #Inserir o registor no primeiro espaço disponivel na led
            #novo registro é menor e gera um no espaço livre
            
            #remover espaço da LED
            self.removerEspacoLED()

            self.file.seek(offset_registro_LED)
            self.file.write(tam_registro.to_bytes(self.RECORD_SIZE_FIELD))
            self.file.write(buffer)
            
            offset_fragmentacao = offset_registro_LED + tam_registro + self.RECORD_SIZE_FIELD
            tam_fragmentacao = tam_registro_LED - tam_registro - self.RECORD_SIZE_FIELD

            
            self.file.seek(offset_fragmentacao)
            n = n_buffer.ljust(tam_fragmentacao, b'\0')
            self.file.write(n)

            if tam_fragmentacao >= self.MIN_SIZE_FRAGMENTATION:
                self.file.seek(offset_fragmentacao)
                self.file.write(tam_fragmentacao.to_bytes(self.RECORD_SIZE_FIELD))
                self.file.write("*".encode())
                self.inserirEspacoLED(offset_fragmentacao, tam_fragmentacao)


    #Finalizado e testado
    def removerRegistro(self, identificador):
        offset, tam_registro = self.buscarRegistro(identificador)[-2:]
        if type(offset) == int:
            self.file.seek(offset+2)
            char_remocao = "*".encode()
            self.file.write(char_remocao)
            self.inserirEspacoLED(offset, tam_registro)

        else:
            return "Registro não está no arquivo"

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

    #Finalizado e testado
    def inserirEspacoLED(self, offset_novo_espaco:int, tam_novo_espaco:int) -> str:
            self.file.seek(0)
            cabecalho = self.file.read(4)
            end_LED = b'\xff\xff\xff\xff'
            
            #Caso 1: LED está vazia
            if cabecalho == end_LED:
                self.file.seek(0)
                self.file.write(struct.pack("I", offset_novo_espaco))
                self.file.seek(offset_novo_espaco+3)
                self.file.write(end_LED)
                return "Caso 1: LED está vazia"
            
            else:
                offset_LED = struct.unpack("I", cabecalho)[0]
                self.file.seek(offset_LED)
                #tam_espaco_LED = struct.unpack("H", self.file.read(2))[0]
                tam_espaco_LED = int.from_bytes(self.file.read(2))
                self.file.seek(1,1)
                next_offset_LED = self.file.read(4)

                #Caso 2: O novo espaço é maior que o primeiro espaço da LED
                if tam_novo_espaco >= tam_espaco_LED:
                    self.file.seek(0)
                    self.file.write(struct.pack("I", offset_novo_espaco))
                    self.file.seek(offset_novo_espaco+3)
                    self.file.write(struct.pack("I", offset_LED))
                    return "Caso 2: O novo espaço é maior que o primeiro espaço da LED"


                offset_LED = cabecalho

                #Caso 3: O novo espaço será inserido no meio da LED
                while next_offset_LED != end_LED:
                    self.file.seek(struct.unpack("I", next_offset_LED)[0])
                    tam_next_offset = int.from_bytes(self.file.read(2))

                    if tam_novo_espaco >= tam_next_offset:
                        self.file.seek(offset_novo_espaco+3)
                        self.file.write(next_offset_LED)
                        self.file.seek(struct.unpack("I", offset_LED)[0]+3)
                        self.file.write(struct.pack("I", offset_novo_espaco))
                        return "Caso 3: O novo espaço será inserido no meio da LED"

                    offset_LED = next_offset_LED
                    self.file.seek(struct.unpack("I", offset_LED)[0]+3)
                    next_offset_LED = self.file.read(4)

                if next_offset_LED == end_LED:
                    #Caso 4: O novo espaço será inserido no final da LED
                    self.file.seek(struct.unpack("I", offset_LED)[0]+3)
                    self.file.write(struct.pack("I", offset_novo_espaco))
                    self.file.seek(offset_novo_espaco+3)
                    self.file.write(end_LED)
                    return "Caso 4: O novo espaço será inserido no final da LED"

    #Finalizado e testado
    def removerEspacoLED(self) -> None:

        self.file.seek(0)
        offset = self.file.read(self.HEADER_SIZE)

        if offset != b'\xff\xff\xff\xff':
            offset = struct.unpack("I", offset)[0]
            self.file.seek(offset)
            self.file.seek(3, 1)
            nova_cabeca = self.file.read(self.HEADER_SIZE)
            self.file.seek(0)
            self.file.write(nova_cabeca)

            return "Espaço removido!"
        
        else:
            return "A LED está vazia!"

    #Finalizado e testado
    def imprimirLED(self) -> None:
        # LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
        # Total: 3 espaços disponíveis
        
        lista: list[list[int]] = []
        self.file.seek(0)
        offset = self.file.read(self.HEADER_SIZE)
        
        if offset == b'\xff\xff\xff\xff':
            return "LED vazia"
        
        while offset != b'\xff\xff\xff\xff':
            offset = struct.unpack("I", offset)[0]
            self.file.seek(offset)
            tam = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            self.file.seek(1, 1)
            lista.append([offset, tam])
            next_offset = self.file.read(self.HEADER_SIZE)
            offset = next_offset
        
        # Imprimir a lista de offsets e tamanhos
        for x in lista:
            print(f"[offset: {x[0]}, tam: {x[1]}] -> ", end="")
        
        print("[offset: -1]")
        print(f"\nTotal: {self.tamanhoLED()} espaços disponíveis")

    #Finalizada e testado
    def tamanhoLED(self) -> int:
        tam_LED:int = 0
        self.file.seek(0)
        offset = self.file.read(self.HEADER_SIZE)

        while offset != b'\xff\xff\xff\xff':
            offset = struct.unpack("I", offset)[0]
            self.file.seek(offset+3)
            offset = self.file.read(self.HEADER_SIZE)      
            tam_LED += 1

        return tam_LED


a = GerenciadorArquivo("9.dat")
a.abirArquivo()

print(a.buscarRegistro(22))
a.inserirRegistro("144|The Sims|2000|Life simulation|Electronic Arts|PC|")
print(a.removerRegistro(99))
print(a.removerRegistro(230))
a.inserirRegistro("181|Pac-Man|1980|Maze|Namco|Arcade|")
a.inserirRegistro("144|The Sims|2000|Life simulation|Electronic Arts|PC|")

print(a.imprimirLED())

a.fecharArquivo()


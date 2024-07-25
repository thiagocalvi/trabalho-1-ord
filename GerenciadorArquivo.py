import struct

class GerenciadorArquivo:
    def __init__(self, path_file:str, header_size=4, record_size_field=2, min_size_fragmentation=10):
        self.path_file = path_file
        self.file = None
        self.operations_file = None
        self.HEADER_SIZE = header_size
        self.MIN_SIZE_FRAGMENTATION = min_size_fragmentation
        self.RECORD_SIZE_FIELD = record_size_field

    def abrirArquivo(self) -> None:
        try:
            self.file = open(self.path_file, 'r+b')
        except:
            raise FileNotFoundError

    def abrirArquivoOperacoes(self, path_operations_file:str) -> None:
        try:
            self.operations_file = open(path_operations_file, 'r')
        except:
            raise FileNotFoundError

    def fecharArquivo(self) -> None:
        self.file.close()
    
    def fecharArquivoOperacoes(self) -> None:
        self.operations_file.close()

    def tamanhoRegistro(self, offset) -> int:
        self.file.seek(offset)
        tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
        return tam_registro
    
    def buscarRegistro(self, identificador:int):
        
        offset = self.HEADER_SIZE
        
        self.file.seek(offset)

        tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
        while tam_registro != 0:
                    
            if self.file.read(1).decode() != "*":
                self.file.seek(-1, 1)
                registro = self.file.read(tam_registro).decode()
                registro_sem_split = registro
                registro = registro.split("|")[:-1]
                
                if identificador == int(registro[0]):

                    return [registro[:-1], registro_sem_split, int(offset), int(tam_registro)]
    
                offset += tam_registro + self.RECORD_SIZE_FIELD
                tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
                
            else:
                
                offset += tam_registro + self.RECORD_SIZE_FIELD
                self.file.seek(offset)
                tam_registro = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            
        

        return "Erro: Registro não encontrado\n", 0

    def inserirRegistro(self, dados_registro:str) -> str:
        dados = dados_registro.split("|")

        n_buffer = b'\0'
        buffer = dados_registro.encode()
        tam_registro = len(buffer)
        self.file.seek(0)

        print(f"Inserção do registro de chave \"{dados[0]}\" ({tam_registro} bytes)")
        
        offset_registro_LED = self.file.read(self.HEADER_SIZE)

        if offset_registro_LED == b'\xff\xff\xff\xff':
            #Inserir registro no final do arquivo
            self.file.seek(0, 2)
            self.file.write(tam_registro.to_bytes(self.RECORD_SIZE_FIELD))
            self.file.write(buffer)
            
            print("Local: fim do arquivo \n")
            return "Registro inserido no final do arquivo"


        offset_registro_LED = struct.unpack("I", offset_registro_LED)[0]
        tam_registro_LED = self.tamanhoRegistro(offset_registro_LED)

        if tam_registro <= tam_registro_LED:
            self.removerEspacoLED()

            if tam_registro_LED - tam_registro - self.RECORD_SIZE_FIELD >= self.MIN_SIZE_FRAGMENTATION:
                offset_fragmentacao = offset_registro_LED + tam_registro + self.RECORD_SIZE_FIELD
                tam_fragmentacao = tam_registro_LED - tam_registro - self.RECORD_SIZE_FIELD
                self.file.seek(offset_fragmentacao)
                self.file.write(tam_fragmentacao.to_bytes(self.RECORD_SIZE_FIELD))
                self.file.write("*".encode())
                n_buffer = n_buffer.ljust(tam_fragmentacao-self.RECORD_SIZE_FIELD-1, b'\0')

                self.inserirEspacoLED(offset_fragmentacao, tam_fragmentacao)
                
                self.file.seek(offset_registro_LED)
                self.file.write(tam_registro.to_bytes(self.RECORD_SIZE_FIELD))
                self.file.write(buffer)

                print(f"Tamanho do espaço reutilizado: {tam_registro_LED} bytes (Sobra de {tam_fragmentacao} bytes)")
                print(f"Local: offset = {offset_registro_LED} bytes ({hex(offset_registro_LED)})\n")

            else:
                self.file.seek(offset_registro_LED+2)
                n_buffer = n_buffer.ljust(tam_registro_LED, b'\0')
                self.file.write(n_buffer)
                self.file.seek(offset_registro_LED+2)
                self.file.write(buffer)

                print(f"Tamanho do espaço reutilizado: {tam_registro_LED} bytes")
                print(f"Local: offset = {offset_registro_LED} bytes ({hex(offset_registro_LED)})\n")
            
        else:
            self.file.seek(0, 2)
            self.file.write(tam_registro.to_bytes(self.RECORD_SIZE_FIELD))
            self.file.write(buffer)
            
            print("Local: fim do arquivo \n")
    
    def removerRegistro(self, identificador) -> str:
        print(f"Remoção do registro de chave \"{identificador}\"")
        offset, tam_registro = self.buscarRegistro(identificador)[-2:]
        
        if type(offset) == int:
            n_buffer = b'\0'
            self.file.seek(offset+2)
            char_remocao = "*".encode()
            self.file.write(char_remocao)
            n_buffer = n_buffer.ljust(tam_registro - 1, b'\0')
            self.file.write(n_buffer)
            self.inserirEspacoLED(offset, tam_registro)
            print(f"Registro removido! ({tam_registro} bytes)")
            print(f"Local: offset = {offset} bytes ({hex(offset)})\n")

        else:
            print("Erro: Registro não encontrado!\n")


    #Leitura do arquivo de operações
    def lerArquivoOperacoes(self):
        
        
        line = self.operations_file.readline()

        if line != "": 
            dados = line.split(maxsplit=1)
            operacao = dados[0]
            dados[1] = dados[1].rstrip('\n')   
            return operacao, dados
        
        
        return "Fim das operações", "Acabou"


    #GerenciadorLED
    def inserirEspacoLED(self, offset_novo_espaco:int, tam_novo_espaco:int):
        end_LED = b'\xff\xff\xff\xff'
        self.file.seek(0)

        if self.file.read(self.HEADER_SIZE) == end_LED:
            self.file.seek(0)
            self.file.write(struct.pack("I", offset_novo_espaco))
            self.file.seek(offset_novo_espaco+3)
            self.file.write(end_LED)
        
        else:
            self.file.seek(0)
            offset_led = struct.unpack("I", self.file.read(self.HEADER_SIZE))[0]
            self.file.seek(offset_led)
            tam_cabeca = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            
            if tam_novo_espaco >= tam_cabeca:
                self.file.seek(offset_novo_espaco+3)
                self.file.write(struct.pack("I", offset_led))
                self.file.seek(0)
                self.file.write(struct.pack("I", offset_novo_espaco))

            else:
                offset_atual = offset_led
                self.file.seek(offset_atual+3)
                prox_offset = self.file.read(self.HEADER_SIZE)
                self.file.seek(struct.unpack("I", prox_offset)[0])
                prox_tam = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))

                while prox_offset != end_LED:
                    
                    if prox_tam <= tam_novo_espaco:
                        self.file.seek(offset_novo_espaco+3)
                        self.file.write(prox_offset)
                        self.file.seek(offset_atual+3)
                        self.file.write(struct.pack("I", offset_novo_espaco))
                        return
                    else:
                        offset_atual = struct.unpack("I", prox_offset)[0]
                        self.file.seek(offset_atual+3)
                        prox_offset = self.file.read(self.HEADER_SIZE)
                        self.file.seek(struct.unpack("I", prox_offset)[0])
                        prox_tam = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
                        

                if prox_offset == end_LED:
                    self.file.seek(offset_atual+3)
                    self.file.write(struct.pack("I", offset_novo_espaco))
                    self.file.seek(offset_novo_espaco+3)
                    self.file.write(end_LED)
                    
    def removerEspacoLED(self) -> str:

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

    def imprimirLED(self) -> str:
        # LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
        # Total: 3 espaços disponíveis
        
        lista: list[list[int]] = []
        self.file.seek(0)
        offset = self.file.read(self.HEADER_SIZE)
        tamanhoLED = 0
        
        if offset == b'\xff\xff\xff\xff':
            print("LED vazia")
        
        while offset != b'\xff\xff\xff\xff':
            offset = struct.unpack("I", offset)[0]
            self.file.seek(offset)
            tam = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
            self.file.seek(1, 1)
            lista.append([offset, tam])
            next_offset = self.file.read(self.HEADER_SIZE)
            offset = next_offset
            tamanhoLED += 1
        
        # Imprimir a lista de offsets e tamanhos
        for x in lista:
            print(f"[offset: {x[0]}, tam: {x[1]}] -> ", end="")
        
        print("[offset: -1]")
        print(f"\nTotal: {tamanhoLED} espaços disponíveis")
class GerenciadorArquivo:
    def __init__(self, file, header_size=4, record_size_field=2, min_size_fragmentation=10) -> None:
        self.file = file
        self.HEADER_SIZE = header_size
        self.MIN_SIZE_FRAGMENTATION = min_size_fragmentation
        self.RECORD_SIZE_FIELD = record_size_field

    def tamanhoEspaco(self, byteOffset) -> int:
        #Retorna o tamanho do registro no byteoffset informado
        self.resetPonteiro()
        self.file.seek(byteOffset)
        tam_registro = self.file.read(2)
        tam_registro = int.from_bytes(tam_registro)
        self.resetPonteiro()
        return tam_registro
    
    def resetPonteiro(self) -> None:
        #reset do ponteiro de L/E
        self.file.seek(0)

    def lerCabecalho(self)-> int:
        self.resetPonteiro()
        cabecalho = self.file.read(self.HEADER_SIZE)
        cabecalho = int.from_bytes(cabecalho)
        return cabecalho

    def escreverCabecalho(self, dado_) -> None:
        if type(dado) != bytes:
            dado = dado_.to_bytes(self.HEADER_SIZE)
        else:
            dado = dado
            
        self.resetPonteiro()
        self.file.write(dado)

    #GerenciadorLED
    def inserirEspacoLED(self, offset_novo_espaco) -> None:
        if self.tamanhoEspaco(offset_novo_espaco) < self.MIN_SIZE_FRAGMENTATION:
            return "Espaço muito pequeno para ser reutilizado"
        
        else:
            index = int.from_bytes(self.lerCabecalho())
            if index == -1:
                self.escreverCabecalho(offset_novo_espaco)
            else:
                self.resetPonteiro()
                self.file.seek(offset_novo_espaco)
                tam_novo_espaco = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
                self.resetPonteiro()

                self.file.seek(index)
                tam_na_LED = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
                self.resetPonteiro()
            
                if tam_novo_espaco >= tam_na_LED:
                    self.file.seek(offset_novo_espaco+3)
                    self.file.write(index.to_bytes(self.HEADER_SIZE))
                    self.escreverCabecalho(offset_novo_espaco.to_bytes(self.HEADER_SIZE))
                else:

                    while index != -1:  
                        self.file.seek(index)
                        tam_index_atual = int.from_bytes(self.file.read(self.RECORD_SIZE_FIELD))
                        self.file.seek(1, 1)
                        next_offset = int.from_bytes(self.file.read(self.HEADER_SIZE))

                        if tam_novo_espaco >= tam_index_atual:
                            self.resetPonteiro()
                            self.file.seek(offset_novo_espaco)
                            self.file.seek(3, 1)
                            self.file.write(next_offset.to_bytes(self.HEADER_SIZE))
                            self.resetPonteiro()
                            self.file.seek(index)
                            self.file.seek(3, 1)
                            self.file.write(offset_novo_espaco.to_bytes(self.HEADER_SIZE))
                            self.resetPonteiro()
                            break

                        elif next_offset == -1:
                            self.resetPonteiro()
                            self.file.seek(index)
                            self.file.seek(3, 1)
                            self.file.write(offset_novo_espaco.to_bytes(self.HEADER_SIZE))
                            self.resetPonteiro()
                            self.file.seek(offset_novo_espaco)
                            self.file.seek(3, 1)
                            end_led = -1
                            self.file.write(end_led.to_bytes(self.HEADER_SIZE))
                            self.resetPonteiro()
                            break

                        index:int = next_offset
                        self.resetPonteiro()

                        #index:int = int.from_bytes(self.file.read(self.HEADER_SIZE))

    def removerEspacoLED(self) -> None:
        #Remove o espaço que esta na cabeça da LED
        #O byteoffset armazenado no ceçalho é substituido pelo byteoffset que o geristro armazenava
        cabeca_led:int = int.from_bytes(self.lerCabecalho())
        if cabeca_led != -1:
            self.file.seek(cabeca_led)
            self.seek(3, 1)
            nova_cabeca:bytes = self.file.read(self.HEADER_SIZE)
            self.escreverCabecalho(nova_cabeca)
            self.resetPonteiro()
            return "Espaço removido!"
        else:
            return "A LED está vazia!"

    def imprimirLED(self) -> None:
        #Imprime a LED no seguinte formato
        # LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
        #Total: 3 espacos disponiveis
        lista:list[list] = []
        index:int = int.from_bytes(self.lerCabecalho())
        while index != -1:
            self.file.seek(index)
            tam = int.from_bytes(self.file.read(2))
            lista.append([index, tam])
            self.file.seek(1)
            index:int = int.from_bytes(self.file.read(self.HEADER_SIZE))
            self.resetPonteiro()
       
        lista.append([f"offset: {index}"])
        self.resetPonteiro()

        for x in lista:
            if x[1] != -1:
                print(f"[offset: {x[0]}, tam: {x[1]}] -> ")
            else:
                print(f"[offset: {x[0]}]")

        print(f"\n Total: {self.quantidadeEspacosDisponiveisLED()} de espaços disponiveis")

    def quantidadeEspacosDisponiveisLED(self) -> int:
        #Retorna a quantidade de espaços disponiveis (tamanho da LED)
        #Percorre toda a LED incrementando uma variavel e retorna essa valor quando chegar no fim da LED
        contador:int = 0
        index:int = int.from_bytes(self.lerCabecalho())
        while index != -1:
            self.file.seek(index)
            tam = int.from_bytes(self.file.read(2))
            self.file.seek(1)
            index:int = int.from_bytes(self.file.read(self.HEADER_SIZE))
            contador += 1
        self.resetPonteiro()
        return contador

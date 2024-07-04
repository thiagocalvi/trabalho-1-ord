import struct

class GerenciadorArquivo:
    HEADER_SIZE = 4
    RECORD_SIZE_FIELD = 2
    LED_ENTRY_SIZE = 4

    def __init__(self, file, LED):
        self.file = file
        self.LED = LED
    
    def abrirArquivo(self, modo:str):
        self.file = open(self.file, modo)

    def fecharArquivo(self):
        self.file.close()

    def lerCabecalho(self):
        self.file.seek(0)
        return struct.unpack('I', self.file.read(self.HEADER_SIZE))[0]

    def escreverCabecalho(self, header_value):
        self.file.seek(0)
        self.file.write(struct.pack('I', header_value))

    def lerRegistro(self, offset):
        self.file.seek(offset)
        record_size = struct.unpack('H', self.file.read(self.RECORD_SIZE_FIELD))[0]
        return self.file.read(record_size)

    def escreverRegistro(self, offset, record_data):
        self.file.seek(offset)
        self.file.write(struct.pack('H', len(record_data)))
        self.file.write(record_data)

    def buscarRegistro(self, identifier):
        header = self.lerCabecalho()
        offset = self.HEADER_SIZE + self.LED_ENTRY_SIZE

        while offset < header:
            self.file.seek(offset)
            


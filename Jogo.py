class Jogo:
    def __init__(self, id, titulo, ano, genero, produtora, plataforma):
        self.id = int(id)
        self.titulo = titulo
        self.ano = int(ano)
        self.genero = genero
        self.produtora = produtora
        self.plataforma = plataforma

    def converterParaBytes(self):
        return f"{self.id}|{self.titulo}|{self.ano}|{self.genero}|{self.produtora}|{self.plataforma}|".encode()

    
    def converterDeBytes(byte_data):
        dados = byte_data.decode().split('|')
        if dados[-1] == '':
            dados == dados[:-1]
        
        if len(dados) != 6:
            raise ValueError("Dados inválidos: número incorreto de campos")
        
        return Jogo(*dados)
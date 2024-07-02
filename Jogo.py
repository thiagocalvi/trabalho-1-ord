class Jogo:
    """Representa um registro de jogo no arquivo."""

    def __init__(self, id, titulo, ano, genero, produtora, plataforma):
        """Inicializa um objeto Jogo com os dados fornecidos."""
        self.id = int(id)
        self.titulo = titulo
        self.ano = int(ano)
        self.genero = genero
        self.produtora = produtora
        self.plataforma = plataforma

    def converte_para_bytes(self):
        """Converte o objeto Jogo para uma representação em bytes."""
        return f"{self.id}|{self.titulo}|{self.ano}|{self.genero}|{self.produtora}|{self.plataforma}|".encode()

    
    def converte_de_bytes(byte_data):
        """Cria um objeto Jogo a partir de uma representação em bytes."""
        dados = byte_data.decode().split('|')
        return dados
        #return Jogo(*dados[:-1])  # Ignora o último campo vazio devido ao '|' final

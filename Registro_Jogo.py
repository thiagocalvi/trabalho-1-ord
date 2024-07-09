class Registro_Jogo:

    def __init__(self, registro: bytes):
        self.registro = registro
    
    def dados_em_string(self) -> str:
        registro_string = self.registro.decode()
        return registro_string

    def identificador(self) -> int:
        # Chave do registro que se encontra no primeiro campo
        reg_str = self.dados_em_string()
        chave = reg_str.split(sep='|')[0]
        chave_int = int(chave)
        return chave_int
    
    def dados_em_binario(self) -> bytes:
        return self.registro
    
    def atributos(self):
        # Informações que estão no registro
        reg_str = self.dados_em_string()
        lista_atributos = reg_str.split(sep='|')
        print(f'Chave/Identificador de registro: {lista_atributos[0]}')
        print(f'Título do jogo: {lista_atributos[1]}')
        print(f'Ano de lançamento: {lista_atributos[2]}')
        print(f'Gênero : {lista_atributos[3]}')
        print(f'Produtora: {lista_atributos[4]}')
        print(f'Platafoma: {lista_atributos[5]}')
    
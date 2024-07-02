import struct
import sys

import Jogo

class GerenciadorArquivo:
    """Gerencia operações no arquivo de dados."""

    # Constantes para o formato do arquivo
    CABECALHO_TAMANHO = 4
    TAMANHO_REGISTRO_BYTES = 2
    PONTEIRO_LED_BYTES = 4
    LIMIAR_SOBRA = 10

    def __init__(self, nome_arquivo):
        """Inicializa o gerenciador com o nome do arquivo de dados."""
        self.nome_arquivo = nome_arquivo
        self.arquivo = None

    def abrir(self):
        """Abre o arquivo de dados para leitura e escrita."""
        try:
            self.arquivo = open(self.nome_arquivo, 'r+b')
        except FileNotFoundError:
            print(f"Erro: O arquivo {self.nome_arquivo} não existe.")
            sys.exit(1)

    def fechar(self):
        """Fecha o arquivo de dados."""
        if self.arquivo:
            self.arquivo.close()

    def ler_cabecalho(self):
        """Lê o cabeçalho do arquivo (ponteiro para o início da LED)."""
        self.arquivo.seek(0)
        return struct.unpack('i', self.arquivo.read(self.CABECALHO_TAMANHO))[0]

    def escrever_cabecalho(self, valor):
        """Escreve o valor do cabeçalho no arquivo."""
        self.arquivo.seek(0)
        self.arquivo.write(struct.pack('i', valor))

    def buscar(self, id):
        """Busca um jogo pelo ID no arquivo."""
        self.arquivo.seek(self.CABECALHO_TAMANHO)
        while True:
            posicao = self.arquivo.tell()
            tamanho_bytes = self.arquivo.read(self.TAMANHO_REGISTRO_BYTES)
            if not tamanho_bytes:
                print(f"Erro: registro não encontrado!")
                return None
            tamanho = struct.unpack('H', tamanho_bytes)[0]
            dados = self.arquivo.read(tamanho)
            jogo = Jogo.from_bytes(dados)
            if jogo.id == id:
                print(f"Busca pelo registro de chave \"{id}\"")
                print(f"{jogo.id}|{jogo.titulo}|{jogo.ano}|{jogo.genero}|{jogo.produtora}|{jogo.plataforma}| ({tamanho} bytes)")
                return posicao, tamanho + self.TAMANHO_REGISTRO_BYTES

    def inserir(self, jogo):
        """Insere um novo jogo no arquivo, utilizando a LED se possível."""
        dados = jogo.to_bytes()
        tamanho = len(dados)
        registro = struct.pack('H', tamanho) + dados

        espaco_disponivel = self.encontrar_espaco_disponivel(len(registro))
        if espaco_disponivel:
            # Insere no espaço encontrado na LED
            offset, tamanho_espaco = espaco_disponivel
            self.arquivo.seek(offset)
            self.arquivo.write(registro)
            sobra = tamanho_espaco - len(registro)
            if sobra > self.LIMIAR_SOBRA:
                self.adicionar_espaco_led(offset + len(registro), sobra)
            print(f"Inserção do registro de chave \"{jogo.id}\" ({tamanho} bytes)")
            print(f"Tamanho do espaço reutilizado: {tamanho_espaco} bytes")
            print(f"Local: offset = {offset} bytes (0x{offset:x})")
            if sobra > self.LIMIAR_SOBRA:
                print(f"Sobra de {sobra} bytes")
        else:
            # Insere no final do arquivo
            self.arquivo.seek(0, 2)  # Move para o final do arquivo
            offset = self.arquivo.tell()
            self.arquivo.write(registro)
            print(f"Inserção do registro de chave \"{jogo.id}\" ({tamanho} bytes)")
            print(f"Local: fim do arquivo")

    def remover(self, id):
        """Remove logicamente um jogo do arquivo e adiciona o espaço à LED."""
        resultado_busca = self.buscar(id)
        if resultado_busca:
            posicao, tamanho = resultado_busca
            self.arquivo.seek(posicao)
            self.arquivo.write(b'\x00' * self.TAMANHO_REGISTRO_BYTES)  # Marca como removido
            self.adicionar_espaco_led(posicao, tamanho)
            print(f"Remoção do registro de chave \"{id}\"")
            print(f"Registro removido! ({tamanho} bytes)")
            print(f"Local: offset = {posicao} bytes (0x{posicao:x})")
        else:
            print(f"Erro: registro não encontrado!")

    def encontrar_espaco_disponivel(self, tamanho_necessario):
        """Encontra o melhor espaço disponível na LED (worst-fit)."""
        cabeca_led = self.ler_cabecalho()
        if cabeca_led == -1:
            return None

        melhor_espaco = None
        melhor_tamanho = 0
        atual = cabeca_led
        anterior = -1

        while atual != -1:
            self.arquivo.seek(atual)
            tamanho_atual = struct.unpack('i', self.arquivo.read(self.PONTEIRO_LED_BYTES))[0]
            proximo = struct.unpack('i', self.arquivo.read(self.PONTEIRO_LED_BYTES))[0]

            if tamanho_atual >= tamanho_necessario and tamanho_atual > melhor_tamanho:
                melhor_espaco = (anterior, atual, proximo)
                melhor_tamanho = tamanho_atual

            anterior = atual
            atual = proximo

        if melhor_espaco:
            ant, atual, prox = melhor_espaco
            self.remover_espaco_led(ant, atual, prox)
            return atual, melhor_tamanho

        return None

    def adicionar_espaco_led(self, offset, tamanho):
        """Adiciona um novo espaço à LED."""
        cabeca_led = self.ler_cabecalho()
        self.arquivo.seek(offset)
        self.arquivo.write(struct.pack('ii', tamanho, cabeca_led))
        self.escrever_cabecalho(offset)

    def remover_espaco_led(self, anterior, atual, proximo):
        """Remove um espaço da LED."""
        if anterior == -1:
            self.escrever_cabecalho(proximo)
        else:
            self.arquivo.seek(anterior + self.PONTEIRO_LED_BYTES)
            self.arquivo.write(struct.pack('i', proximo))

    def imprimir_led(self):
        """Imprime a estrutura atual da LED."""
        print("LED ->", end=" ")
        cabeca_led = self.ler_cabecalho()
        atual = cabeca_led
        count = 0

        while atual != -1:
            self.arquivo.seek(atual)
            tamanho = struct.unpack('i', self.arquivo.read(self.PONTEIRO_LED_BYTES))[0]
            proximo = struct.unpack('i', self.arquivo.read(self.PONTEIRO_LED_BYTES))[0]
            print(f"[offset: {atual}, tam: {tamanho}] ->", end=" ")
            atual = proximo
            count += 1

        print("[offset: -1]")
        print(f"Total: {count} espacos disponiveis")
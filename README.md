# Primeiro Trabalho da Disciplina de Organização e Recuperação de Dados


## Descrição do Trabalho
O arquivo **dados.dat** possui informações sobre jogos. Os dados dos jogos estão armazenados em registros de tamanho variável, em formato similar ao utilizado nas aulas práticas. O arquivo possui um cabeçalho de 4 bytes e os campos de tamanho dos registros têm 2 bytes. Cada jogo possui os seguintes campos:

1. IDENTIFICADOR do jogo (utilizado como chave primária);
1. TÍTULO;
1. ANO;
1. GÊNERO;
1. PRODUTORA;
1. PLATAFORMA.

Dado o arquivo **dados.dat**, o seu programa deverá oferecer   as seguintes funcionalidades principais:
* Busca de um jogo pelo IDENTIFICADOR;
* Inserção de um novo jogo;
* Remoção de um jogo.

As operações a serem realizadas em determinada execução serão especificadas em um **arquivo de operações**, o qual será passado ao programa como um parâmetro. Dessa forma, o programa **não possuirá interface com o usuário e executará as operações na sequência em que estiverem especificadas no arquivo de operações**. 

A execução do arquivo de operações será acionada pela linha de comando, sendo ***-e*** a flag que sinaliza o modo de execução e arquivo_operacoes o nome do arquivo que contém as operações a serem executadas. Para simplificar o processamento do arquivo de operações, considere que ele sempre será fornecido corretamente.

As instruções devem estar da seguinte forma no arquivo de operações:
```
b 22 #bucas pelo registro 22
i 147|Resident Evil 2|1998|Survival horror|Capcom|PlayStation| #insere um registro no identificador 147
r 99 #remove registro 99
r 230 #remove registro 230
i 181|Pac-Man|1980|Maze|Namco|Arcade| #insere um registro no identificador 181
i 144|The Sims|2000|Life simulation|Electronic Arts|PC| #insere um registro no identificador 144
```

* b -> Buscar
* i -> Inserção
* r -> Remoção


Cada operação que for executada deve ser apresentada de forma formatada no console:
```
Busca pelo registro de chave "22"
22|Tetris|1984|Puzzle|Elorg|Electronika 60| (43 bytes)

Inserção do registro de chave "147" (60 bytes)
Local: fim do arquivo

Remoção do registro de chave "99"
Registro removido! (94 bytes)
Local: offset = 6290 bytes (0x1892)

Remoção do registro de chave "230"
Erro: registro não encontrado!

Inserção do registro de chave "181" (35 bytes)
Tamanho do espaço reutilizado: 94 bytes (Sobra de 57 bytes)
Local: offset = 6290 bytes (0x1892)

Inserção do registro de chave "144" (53 bytes)
Tamanho do espaço reutilizado: 57 bytes
Local: offset = 6327 bytes (0x18b7)
```

### Gerenciamento de Espaços Disponívei
As alterações que venham a ocorrer no arquivo dados.dat deverão ser persistentes. A remoção de registros será lógica e o espaço resultante da remoção deverá ser inserido na Lista de Espaços Disponíveis (LED). A LED deverá ser mantida no próprio arquivo e os ponteiros da LED devem ser gravados como números inteiros de 4 bytes. O seu programa deverá implementar todos os mecanismos necessários para o gerenciamento da LED e reutilização dos espaços disponíveis utilizando a estratégia pior ajuste (worst-fit).

No momento da inserção de novos registros, a LED deverá ser consultada. Se existir um espaço disponível para a inserção, o novo registro deverá ser inserido nesse espaço. Sobras de espaço resultantes da inserção deverão ser reinseridas na LED, a menos que sejam menores do que um determinado limiar (p.e., 10 bytes). Caso não seja encontrado na LED um espaço adequado para o novo registro, ele deverá ser inserido no final do arquivo.

Deve ser implementado uma funcionalidade para imprimir a LED, também sendo chamada pela linha de comando com a flag -p.

Os dados devem ser apresentados da seguinte forma:
```
LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
Total: 3 espacos disponiveis
```

## Definição dos métodos da classe GerenciadorArquivo

# New version
## Gerenciador de Arquivo

## Descrição

A classe `GerenciadorArquivo` implementa um gerenciador de arquivo binário que permite manipular registros de forma eficiente e controlar fragmentação por meio de uma Lista de Espaços Disponíveis (LED). A classe permite operações de inserção, busca, remoção de registros, bem como a manipulação da LED.

## Métodos

#### `__init__(self, path_file: str, header_size=4, record_size_field=2, min_size_fragmentation=10) -> None`

Inicializa a classe `GerenciadorArquivo`.

- `path_file` (str): O caminho do arquivo a ser gerenciado.
- `header_size` (int): O tamanho do cabeçalho do arquivo.
- `record_size_field` (int): O tamanho do campo que armazena o tamanho dos registros.
- `min_size_fragmentation` (int): O tamanho mínimo da fragmentação.

#### `abrirArquivo(self) -> None`

Abre o arquivo binário para leitura e escrita em modo binário. Lança uma exceção `FileNotFoundError` se o arquivo não for encontrado.

#### `abrirArquivoOperacoes(self, operations_file: str) -> None`

Abre o arquivo de operações em modo de leitura. Lança uma exceção `FileNotFoundError` se o arquivo não for encontrado.

- `operations_file` (str): O caminho do arquivo de operações.

#### `fecharArquivo(self) -> None`

Fecha o arquivo binário aberto.

#### `fecharArquivoOperacoes(self) -> None`

Fecha o arquivo de operações aberto.

#### `tamanhoRegistro(self, offset: int) -> int`

Retorna o tamanho do registro no offset especificado.

- `offset` (int): O offset do registro no arquivo.
- Funciona posicionando o ponteiro de leitura no offset fornecido e lendo o tamanho do registro a partir daí.

#### `buscarRegistro(self, identificador: int) -> Union[list, str]`

Busca um registro pelo identificador.

- `identificador` (int): O identificador do registro a ser buscado.
- Percorre o arquivo a partir do cabeçalho, lê o tamanho de cada registro e verifica se o registro não está marcado como removido.
- Se encontrar o registro, retorna uma lista contendo os dados do registro, offset e tamanho.
- Retorna "Registro não encontrado" se não encontrar o registro.

#### `inserirRegistro(self, dados_registro: str) -> str`

Insere um novo registro no arquivo.

- `dados_registro` (str): Os dados do registro a ser inserido.
- Verifica se há espaço disponível na LED para inserir o registro. Caso contrário, insere no final do arquivo.
- Se o espaço disponível na LED for menor que o necessário, cria um novo espaço de fragmentação.
- Retorna uma mensagem indicando se o registro foi inserido no final do arquivo ou em um espaço disponível na LED.

#### `removerRegistro(self, identificador: int) -> str`

Remove um registro pelo identificador.

- `identificador` (int): O identificador do registro a ser removido.
- Busca o registro pelo identificador. Se encontrado, marca o registro como removido.
- Adiciona o espaço do registro removido à LED.
- Retorna uma mensagem indicando se o registro foi removido ou se não foi encontrado no arquivo.

#### `percorrerArquivo(self) -> None`

Percorre e imprime os registros do arquivo para fins de teste.

- Lê e imprime cada registro a partir do cabeçalho do arquivo até o final, mostrando os offsets dos registros.

#### `lerArquivoOperacoes(self) -> Tuple[str, str]`

Lê uma linha do arquivo de operações.

- Retorna uma tupla contendo a operação (primeiro caractere da linha) e os dados (restante da linha).
- Retorna "Fim das operações" se alcançar o final do arquivo de operações.

#### `inserirEspacoLED(self, offset_novo_espaco: int, tam_novo_espaco: int) -> str`

Insere um novo espaço na LED.

- `offset_novo_espaco` (int): O offset do novo espaço.
- `tam_novo_espaco` (int): O tamanho do novo espaço.
- Verifica se a LED está vazia. Se estiver, insere o novo espaço como o primeiro.
- Caso contrário, insere o novo espaço na posição correta na LED, mantendo a ordem crescente de tamanho.
- Retorna uma mensagem indicando em qual caso a inserção ocorreu (vazia, maior, meio ou final da LED).

#### `removerEspacoLED(self) -> str`

Remove o primeiro espaço disponível na LED.

- Atualiza o cabeçalho do arquivo para apontar para o próximo espaço disponível na LED.
- Retorna uma mensagem indicando que o espaço foi removido ou que a LED está vazia.

#### `imprimirLED(self) -> str`

Imprime a LED e o número de espaços disponíveis.

- Percorre a LED a partir do cabeçalho e coleta os offsets e tamanhos de cada espaço disponível.
- Imprime a lista de espaços disponíveis e o total de espaços.
- Retorna uma mensagem indicando o estado da LED.

#### `tamanhoLED(self) -> int`

Retorna o número de espaços disponíveis na LED.

- Percorre a LED e conta o número de espaços disponíveis.
- Retorna o total de espaços na LED.

## Exemplo de Uso

```python
a = GerenciadorArquivo("1.dat")
a.abrirArquivo()

print(a.buscarRegistro(22))
a.inserirRegistro("144|The Sims|2000|Life simulation|Electronic Arts|PC|")
print(a.removerRegistro(99))
print(a.removerRegistro(230))
a.inserirRegistro("181|Pac-Man|1980|Maze|Namco|Arcade|")
a.inserirRegistro("144|The Sims|2000|Life simulation|Electronic Arts|PC|")

print(a.imprimirLED())

a.fecharArquivo()
```

# Old version

## GerenciadorArquivo

**lerCabecalho:**
* Não têm parâmetros.
* Deve ler o cabeçalho do arquivo **dados.dat**.
* Como o cabeçalho do arquivo guarda a cabeça da LED deve converter esse valor de bytes para um inteiro e retornar esse valor.
* Retorna um inteiro.

**tamanhoEspaco:**
* Recebe como parâmetro o byte offset de um registro
* Retorna o tamanho do registro no byte offset informado.
* Retorna um inteiro.

**resetPonteiro:**
* Não têm parâmetros.
* Posiciona o ponteiro de Leitura/Escrita no inicio do arquivo.
* Sem retorno.

### GerenciadorLED
Os métodos referente ao GerenciadorLED são usados unicamente para manipular a LED que está armazenada no arquivo **dados.dat**.

Esses métodos estão logo abaixo do comentário #GerenciadorLED

**inserirEspacoLED:**
* Recebe como parâmetro o byte offset do novo registro que será inserido na LED.
* Verifica se o tamanho do novo espaço é menor que o tamanho minimo de fragmentação, se for menor retorna "Espaço muito pequeno para ser reutilizado".
* Insere o novo espaço na LED mantendo a LED ordenada de forma decrescente, estratégia pior ajuste (worst-fit).
* Sem retorno.

**removerEspacoLED:**
* Não têm parâmetros.
* Remove o espaço que está na cabeça da LED.
* Adiciona o byte offset do próximo espaço da LED na cabeça da LED.
* Retorna "Espaço removido".
* Se a LED estiver vazia retorna "A LED está vazia!",

**imprimirLED:**
* Não têm parâmetros.
* Imprime os espaços que estão armazenados na LED.
* Sem retorno.

**quantidadeEspacosDisponiveisLED:**
* Não têm parâmetros.
* Contabiliza a quantidade espaços que estão armazenados na LED.
* Retorna um inteiro

## Definição dos métodos da classe Registro_Jogo

### Registro_Jogo
Os métodos referentes a classe Registro_Jogo são unicamente para ler um registro do arquivos dados.dat e operação.txt e identificar seus atributos 

**dados_em_string**
* Não tem parâmetros
* Retorna o registro na forma de uma string

**identificador**
* Não tem parâmetros 
* Obtém-se o identificador do registro, o qual está em seu primeiro campo
* Retorna o identificador do registro na forma de um inteiro

**dados_em_bytes**
* Não tem parâmetros
* Retorna o registro em sua forma binária/bytes

**Atributos**
* Não tem parâmetros
* Separa os campos da string e os escreves em relação ao que cada campo representa
* Sem retorno
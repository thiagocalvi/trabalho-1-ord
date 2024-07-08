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

### Gerenciamento de Espaços Disponíveis
As alterações que venham a ocorrer no arquivo dados.dat deverão ser persistentes. A remoção de registros será lógica e o espaço resultante da remoção deverá ser inserido na Lista de Espaços Disponíveis (LED). A LED deverá ser mantida no próprio arquivo e os ponteiros da LED devem ser gravados como números inteiros de 4 bytes. O seu programa deverá implementar todos os mecanismos necessários para o gerenciamento da LED e reutilização dos espaços disponíveis utilizando a estratégia pior ajuste (worst-fit).

No momento da inserção de novos registros, a LED deverá ser consultada. Se existir um espaço disponível para a inserção, o novo registro deverá ser inserido nesse espaço. Sobras de espaço resultantes da inserção deverão ser reinseridas na LED, a menos que sejam menores do que um determinado limiar (p.e., 10 bytes). Caso não seja encontrado na LED um espaço adequado para o novo registro, ele deverá ser inserido no final do arquivo.

Deve ser implementado uma funcionalidade para imprimir a LED, também sendo chamada pela linha de comando com a flag -p.

Os dados devem ser apresentados da seguinte forma:
```
LED -> [offset: 4, tam: 80] -> [offset: 218, tam: 50] -> [offset: 169, tam: 47] -> [offset: -1]
Total: 3 espacos disponiveis
```

## Definição dos métodos da classe GerenciadorArquivo

**lerCabecalho:**
* Não têm parâmetros.
* Deve ler o cabeçalho do arquivo **dados.dat**.
* Como o cabeçalho do arquivo guarda a cabeça da LED deve converter esse valor de bytes para um inteiro e retornar esse valor.
* Retorna um inteiro.



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

**tamanhoEspaco:**
* Recebe como parâmetro o byte offset de um registro
* Retorna o tamanho do registro no byte offset informado.
* Retorna um inteiro.

**resetPonteiro:**
* Não têm parâmetros.
* Posiciona o ponteiro de Leitura/Escrita no inicio do arquivo.
* Sem retorno.
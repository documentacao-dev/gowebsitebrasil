<!--{
  "ia-translated": true,
  "Title": "Tutorial: Acessando um banco de dados relacional",
  "Breadcrumb": true
}-->

Este tutorial apresenta o básico de como acessar um banco de dados relacional
com Go e o pacote `database/sql` da sua biblioteca padrão.

Você vai aproveitar melhor este tutorial se já tiver uma familiaridade básica
com Go e suas ferramentas. Se este for o seu primeiro contato com Go, veja
[Tutorial: Primeiros passos com Go](/doc/tutorial/getting-started)
para uma introdução rápida.

O pacote [`database/sql`](https://pkg.go.dev/database/sql) que você vai usar
inclui tipos e funções para conectar a bancos de dados, executar transações,
cancelar uma operação em andamento e mais. Para mais detalhes sobre como usar o
pacote, veja [Acessando bancos de dados](/doc/database/index).

Neste tutorial, você vai criar um banco de dados e depois escrever código para
acessá-lo. O seu projeto de exemplo será um repositório de dados sobre discos
de jazz antigos.

Neste tutorial, você vai avançar pelas seguintes seções:

1. Criar uma pasta para o seu código.
2. Configurar um banco de dados.
3. Importar o driver do banco de dados.
4. Obter um handle do banco de dados e conectar.
5. Consultar várias linhas.
6. Consultar uma única linha.
7. Adicionar dados.

**Nota:** Para outros tutoriais, veja [Tutoriais](/doc/tutorial/index.html).

## Pré-requisitos {#prerequisites}

*   **Uma instalação do sistema de gerenciamento de banco de dados relacional
    [MySQL](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/)
    (DBMS).**
*   **Uma instalação do Go.** Para as instruções de instalação, veja
    [Instalando o Go](/doc/install).
*   **Uma ferramenta para editar seu código.** Qualquer editor de texto que você
    tenha vai funcionar bem.
*   **Um terminal de comandos.** O Go funciona bem em qualquer terminal no Linux
    e no Mac, e no PowerShell ou cmd no Windows.

## Criar uma pasta para o seu código {#create_folder}

Para começar, crie uma pasta para o código que você vai escrever.

1. Abra um prompt de comando e vá para o seu diretório home.

    No Linux ou Mac:

    ```
    $ cd
    ```

    No Windows:

    ```
    C:\> cd %HOMEPATH%
    ```

    Pelo resto do tutorial, vamos mostrar um $ como prompt. Os comandos que
    usamos também vão funcionar no Windows.

2. No prompt de comando, crie um diretório para o seu código chamado
    data-access.

    ```
    $ mkdir data-access
    $ cd data-access
    ```


3. Crie um módulo no qual você possa gerenciar as dependências que vai adicionar
    durante este tutorial.

    Execute o comando `go mod init`, informando o caminho do módulo do seu novo
    código.

    ```
    $ go mod init example/data-access
    go: creating new go.mod: module example/data-access
    ```

    Este comando cria um arquivo go.mod no qual as dependências que você
    adicionar serão listadas para rastreamento. Para saber mais, veja
    [Gerenciando dependências](/doc/modules/managing-dependencies).

    **Nota:** No desenvolvimento real, você especificaria um caminho de módulo
    mais específico para as suas próprias necessidades. Para saber mais, veja
    [Gerenciando dependências](/doc/modules/managing-dependencies#naming_module).

Em seguida, você vai criar um banco de dados.

## Configurar um banco de dados {#set_up_database}

Nesta etapa, você vai criar o banco de dados com o qual vai trabalhar. Você vai
usar a CLI do próprio DBMS para criar o banco e a tabela, além de adicionar
dados.

Você vai criar um banco de dados com dados sobre gravações de jazz antigas em
vinil.

O código aqui usa a [CLI do MySQL](https://dev.mysql.com/doc/refman/8.0/en/mysql.html),
mas a maioria dos DBMS tem a sua própria CLI com recursos semelhantes.

1. Abra um novo prompt de comando.
2. Na linha de comando, entre no seu DBMS, como no exemplo a seguir para o
    MySQL.

    ```
    $ mysql -u root -p
    Enter password:

    mysql>
    ```

3. No prompt de comando do `mysql`, crie um banco de dados.

    ```
    mysql> create database recordings;
    ```

4. Mude para o banco de dados que você acabou de criar para poder adicionar
    tabelas.

    ```
    mysql> use recordings;
    Database changed
    ```

5. No seu editor de texto, na pasta data-access, crie um arquivo chamado
    create-tables.sql para guardar o script SQL que adiciona as tabelas.
6. No arquivo, cole o código SQL a seguir e salve o arquivo.

    ```
    DROP TABLE IF EXISTS album;
    CREATE TABLE album (
      id         INT AUTO_INCREMENT NOT NULL,
      title      VARCHAR(128) NOT NULL,
      artist     VARCHAR(255) NOT NULL,
      price      DECIMAL(5,2) NOT NULL,
      PRIMARY KEY (`id`)
    );

    INSERT INTO album
      (title, artist, price)
    VALUES
      ('Blue Train', 'John Coltrane', 56.99),
      ('Giant Steps', 'John Coltrane', 63.99),
      ('Jeru', 'Gerry Mulligan', 17.99),
      ('Sarah Vaughan', 'Sarah Vaughan', 34.98);
    ```

    Neste código SQL, você:

    *   Exclui (drop) uma tabela chamada `album`. Executar este comando primeiro
        facilita rodar o script de novo mais tarde, se você quiser recomeçar com
        a tabela.

    *   Cria uma tabela `album` com quatro colunas: `title`, `artist` e `price`.
        O valor de `id` de cada linha é criado automaticamente pelo DBMS.

    *   Adiciona quatro linhas com valores.

7. No prompt de comando do `mysql`, execute o script que você acabou de criar.

    Você vai usar o comando `source` na seguinte forma:

    ```
    mysql> source /caminho/para/create-tables.sql
    ```

8. No prompt de comando do seu DBMS, use uma instrução `SELECT` para verificar
    se você criou a tabela com os dados com sucesso.

    ```
    mysql> select * from album;
    +----+---------------+----------------+-------+
    | id | title         | artist         | price |
    +----+---------------+----------------+-------+
    |  1 | Blue Train    | John Coltrane  | 56.99 |
    |  2 | Giant Steps   | John Coltrane  | 63.99 |
    |  3 | Jeru          | Gerry Mulligan | 17.99 |
    |  4 | Sarah Vaughan | Sarah Vaughan  | 34.98 |
    +----+---------------+----------------+-------+
    4 rows in set (0.00 sec)
    ```

Em seguida, você vai escrever um código em Go para conectar e poder fazer
consultas.

## Encontrar e importar um driver de banco de dados {#import_driver}

Agora que você tem um banco de dados com alguns dados, vamos começar o seu código
em Go.

Encontre e importe um driver de banco de dados que vai traduzir as requisições
que você faz pelas funções do pacote `database/sql` em requisições que o banco
de dados entende.

1. No seu navegador, acesse a página da wiki [SQLDrivers](/wiki/SQLDrivers)
    para identificar um driver que você possa usar.

    Use a lista da página para identificar o driver que você vai usar. Para
    acessar o MySQL neste tutorial, você vai usar o
    [Go-MySQL-Driver](https://github.com/go-sql-driver/mysql/).

2. Anote o nome do pacote do driver -- aqui, `github.com/go-sql-driver/mysql`.

3. Usando o seu editor de texto, crie um arquivo no qual escrever o seu código
    em Go e salve o arquivo como main.go na pasta data-access que você criou
    antes.

4. No main.go, cole o código a seguir para importar o pacote do driver.

    ```
    package main

    import "github.com/go-sql-driver/mysql"
    ```

    Neste código, você:

    *   Adiciona o seu código a um pacote `main` para poder executá-lo de forma
        independente.

    *   Importa o driver do MySQL `github.com/go-sql-driver/mysql`.

Com o driver importado, você vai começar a escrever o código para acessar o
banco de dados.

## Obter um handle do banco de dados e conectar {#get_handle}

Agora escreva um código em Go que dê acesso ao banco de dados por meio de um
handle.

Você vai usar um ponteiro para uma struct `sql.DB`, que representa o acesso a um
banco de dados específico.

#### Escrever o código

1. No main.go, abaixo do código `import` que você acabou de adicionar, cole o
    código Go a seguir para criar um handle do banco de dados.

    ```
    var db *sql.DB

    func main() {
    	// Capture connection properties.
    	cfg := mysql.NewConfig()
    	cfg.User = os.Getenv("DBUSER")
    	cfg.Passwd = os.Getenv("DBPASS")
    	cfg.Net = "tcp"
    	cfg.Addr = "127.0.0.1:3306"
    	cfg.DBName = "recordings"

    	// Get a database handle.
    	var err error
    	db, err = sql.Open("mysql", cfg.FormatDSN())
    	if err != nil {
    		log.Fatal(err)
    	}

    	pingErr := db.Ping()
    	if pingErr != nil {
    		log.Fatal(pingErr)
    	}
    	fmt.Println("Connected!")
    }
    ```

    Neste código, você:

    *   Declara uma variável `db` do tipo [`*sql.DB`](https://pkg.go.dev/database/sql#DB).
        Este é o seu handle do banco de dados.

        Tornar `db` uma variável global simplifica este exemplo. Em produção, você
        evitaria a variável global, por exemplo passando a variável para as
        funções que precisam dela ou encapsulando-a em uma struct.

    *   Usa o [`Config`](https://pkg.go.dev/github.com/go-sql-driver/mysql#Config)
        do driver MySQL -- e o método [`FormatDSN`](https://pkg.go.dev/github.com/go-sql-driver/mysql#Config.FormatDSN)
        do tipo -- para reunir as propriedades de conexão e formatá-las em um DSN
        para uma string de conexão.

        A struct `Config` deixa o código mais fácil de ler do que uma string de
        conexão seria.

    *   Chama [`sql.Open`](https://pkg.go.dev/database/sql#Open)
        para inicializar a variável `db`, passando o valor retornado por
        `FormatDSN`.

    *   Verifica se há um erro de `sql.Open`. Ele poderia falhar se, por
        exemplo, os detalhes da conexão com o banco não estivessem bem formados.

        Para simplificar o código, você está chamando `log.Fatal` para encerrar
        a execução e imprimir o erro no console. Em código de produção, você vai
        querer tratar os erros de forma mais elegante.

    *   Chama [`DB.Ping`](https://pkg.go.dev/database/sql#DB.Ping) para
        confirmar que a conexão com o banco de dados funciona. Em tempo de
        execução, o `sql.Open` pode não conectar imediatamente, dependendo do
        driver. Você está usando `Ping` aqui para confirmar que o pacote
        `database/sql` consegue conectar quando precisar.

    *   Verifica se há um erro de `Ping`, caso a conexão tenha falhado.

    *   Imprime uma mensagem se `Ping` conectar com sucesso.

2. Perto do topo do arquivo main.go, logo abaixo da declaração do pacote, importe
    os pacotes de que você vai precisar para dar suporte ao código que acabou de
    escrever.

    O topo do arquivo deve ficar assim:

    ```
    package main

    import (
    	"database/sql"
    	"fmt"
    	"log"
    	"os"

    	"github.com/go-sql-driver/mysql"
    )
    ```

3. Salve o main.go.

#### Executar o código

1. Comece a rastrear o módulo do driver MySQL como dependência.

    Use o [`go get`](/cmd/go/#hdr-Add_dependencies_to_current_module_and_install_them)
    para adicionar o módulo github.com/go-sql-driver/mysql como dependência do
    seu próprio módulo. Use o argumento ponto para significar "obter as
    dependências do código no diretório atual".

    ```
    $ go get .
    go: added filippo.io/edwards25519 v1.1.0
    go: added github.com/go-sql-driver/mysql v1.8.1
    ```

    O Go baixou essa dependência porque você a adicionou à declaração `import`
    na etapa anterior. Para saber mais sobre o rastreamento de dependências, veja
    [Adicionando uma dependência](/doc/modules/managing-dependencies#adding_dependency).

2. No prompt de comando, defina as variáveis de ambiente `DBUSER` e `DBPASS` para
    uso pelo programa em Go.

    No Linux ou Mac:

    ```
    $ export DBUSER=username
    $ export DBPASS=password
    ```

    No Windows:

    ```
    C:\Users\you\data-access> set DBUSER=username
    C:\Users\you\data-access> set DBPASS=password
    ```

3. Na linha de comando, no diretório que contém o main.go, execute o código
    digitando `go run` com um argumento ponto para significar "execute o pacote
    no diretório atual".

    ```
    $ go run .
    Connected!
    ```

Você consegue conectar! Em seguida, vamos consultar alguns dados.

## Consultar várias linhas {#multiple_rows}

Nesta seção, você vai usar Go para executar uma consulta SQL projetada para
retornar várias linhas.

Para instruções SQL que podem retornar várias linhas, você usa o método `Query`
do pacote `database/sql` e depois percorre as linhas retornadas. (Você vai
aprender a consultar uma única linha mais adiante, na seção
[Consultar uma única linha](#single_row).)
#### Escrever o código

1. No main.go, logo acima de `func main`, cole a definição a seguir de uma
    struct `Album`. Você vai usá-la para guardar os dados das linhas retornadas
    pela consulta.

    ```
    type Album struct {
    	ID     int64
    	Title  string
    	Artist string
    	Price  float32
    }
    ```

2. Abaixo de `func main`, cole a função `albumsByArtist` a seguir para consultar
    o banco de dados.

    ```
    // albumsByArtist queries for albums that have the specified artist name.
    func albumsByArtist(name string) ([]Album, error) {
    	// An albums slice to hold data from returned rows.
    	var albums []Album

    	rows, err := db.Query("SELECT * FROM album WHERE artist = ?", name)
    	if err != nil {
    		return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
    	}
    	defer rows.Close()
    	// Loop through rows, using Scan to assign column data to struct fields.
    	for rows.Next() {
    		var alb Album
    		if err := rows.Scan(&alb.ID, &alb.Title, &alb.Artist, &alb.Price); err != nil {
    			return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
    		}
    		albums = append(albums, alb)
    	}
    	if err := rows.Err(); err != nil {
    		return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
    	}
    	return albums, nil
    }
    ```

    Neste código, você:

    *   Declara uma fatia `albums` do tipo `Album` que você definiu. Ela vai
        guardar os dados das linhas retornadas. Os nomes e tipos dos campos da
        struct correspondem aos nomes e tipos das colunas do banco de dados.

    *   Usa [`DB.Query`](https://pkg.go.dev/database/sql#DB.Query) para
        executar uma instrução `SELECT` que consulta os álbuns com o nome de
        artista especificado.

        O primeiro parâmetro de `Query` é a instrução SQL. Depois dele, você pode
        passar zero ou mais parâmetros de qualquer tipo. Eles servem de lugar
        para você informar os valores dos parâmetros na sua instrução SQL. Ao
        separar a instrução SQL dos valores dos parâmetros (em vez de concatená-
        los com, por exemplo, `fmt.Sprintf`), você permite que o pacote
        `database/sql` envie os valores separados do texto SQL, eliminando
        qualquer risco de injeção de SQL.

    *   Adia o fechamento de `rows` (com `defer`) para que os recursos que ele
        mantém sejam liberados quando a função terminar.

    *   Percorre as linhas retornadas, usando
        [`Rows.Scan`](https://pkg.go.dev/database/sql#Rows.Scan) para
        atribuir os valores das colunas de cada linha aos campos da struct
        `Album`.

        `Scan` recebe uma lista de ponteiros para valores Go, onde os valores das
        colunas serão escritos. Aqui, você passa ponteiros para os campos da
        variável `alb`, criada com o operador `&`. `Scan` escreve por meio dos
        ponteiros para atualizar os campos da struct.

    *   Dentro do laço, verifica se há um erro ao copiar os valores das colunas
        para os campos da struct.

    *   Dentro do laço, adiciona o novo `alb` à fatia `albums`.

    *   Depois do laço, verifica se há um erro na consulta como um todo, usando
        `rows.Err`. Repare que, se a própria consulta falhar, verificar o erro
        aqui é a única forma de descobrir que os resultados estão incompletos.

3. Atualize a sua função `main` para chamar `albumsByArtist`.

    No final de `func main`, adicione o código a seguir.

    ```
    albums, err := albumsByArtist("John Coltrane")
    if err != nil {
    	log.Fatal(err)
    }
    fmt.Printf("Albums found: %v\n", albums)
    ```

    No código novo, você agora:

    *   Chama a função `albumsByArtist` que você adicionou, atribuindo o valor
        retornado a uma nova variável `albums`.

    *   Imprime o resultado.

#### Executar o código

Na linha de comando, no diretório que contém o main.go, execute o código.

```
$ go run .
Connected!
Albums found: [{1 Blue Train John Coltrane 56.99} {2 Giant Steps John Coltrane 63.99}]
```

Em seguida, você vai consultar uma única linha.

## Consultar uma única linha {#single_row}

Nesta seção, você vai usar Go para consultar uma única linha no banco de dados.

Para instruções SQL que você sabe que vão retornar no máximo uma linha, você pode
usar `QueryRow`, que é mais simples do que usar um laço com `Query`.

#### Escrever o código

1. Abaixo de `albumsByArtist`, cole a função `albumByID` a seguir.

    ```
    // albumByID queries for the album with the specified ID.
    func albumByID(id int64) (Album, error) {
    	// An album to hold data from the returned row.
    	var alb Album

    	row := db.QueryRow("SELECT * FROM album WHERE id = ?", id)
    	if err := row.Scan(&alb.ID, &alb.Title, &alb.Artist, &alb.Price); err != nil {
    		if err == sql.ErrNoRows {
    			return alb, fmt.Errorf("albumsById %d: no such album", id)
    		}
    		return alb, fmt.Errorf("albumsById %d: %v", id, err)
    	}
    	return alb, nil
    }
    ```

    Neste código, você:

    *   Usa [`DB.QueryRow`](https://pkg.go.dev/database/sql#DB.QueryRow)
        para executar uma instrução `SELECT` que consulta um álbum com o ID
        especificado.

        Ele retorna um `sql.Row`. Para simplificar o código que chama a função
        (o seu código!), `QueryRow` não retorna um erro. Em vez disso, ele se
        encarrega de devolver qualquer erro da consulta (como `sql.ErrNoRows`)
        depois, a partir de `Rows.Scan`.

    *   Usa [`Row.Scan`](https://pkg.go.dev/database/sql#Row.Scan) para copiar
        os valores das colunas para os campos da struct.

    *   Verifica se há um erro de `Scan`.

        O erro especial `sql.ErrNoRows` indica que a consulta não retornou
        linhas. Normalmente, vale a pena substituir esse erro por um texto mais
        específico, como "no such album" aqui.

2. Atualize `main` para chamar `albumByID`.

    No final de `func main`, adicione o código a seguir.

    ```
    // Hard-code ID 2 here to test the query.
    alb, err := albumByID(2)
    if err != nil {
    	log.Fatal(err)
    }
    fmt.Printf("Album found: %v\n", alb)
    ```

    No código novo, você agora:

    *   Chama a função `albumByID` que você adicionou.

    *   Imprime o ID do álbum retornado.

#### Executar o código

Na linha de comando, no diretório que contém o main.go, execute o código.


```
$ go run .
Connected!
Albums found: [{1 Blue Train John Coltrane 56.99} {2 Giant Steps John Coltrane 63.99}]
Album found: {2 Giant Steps John Coltrane 63.99}
```

Em seguida, você vai adicionar um álbum ao banco de dados.

## Adicionar dados {#add_data}

Nesta seção, você vai usar Go para executar uma instrução SQL `INSERT` que
adiciona uma nova linha ao banco de dados.

Você já viu como usar `Query` e `QueryRow` com instruções SQL que retornam
dados. Para executar instruções SQL que _não_ retornam dados, você usa `Exec`.

#### Escrever o código

1. Abaixo de `albumByID`, cole a função `addAlbum` a seguir para inserir um novo
    álbum no banco de dados e, em seguida, salve o main.go.

    ```
    // addAlbum adds the specified album to the database,
    // returning the album ID of the new entry
    func addAlbum(alb Album) (int64, error) {
    	result, err := db.Exec("INSERT INTO album (title, artist, price) VALUES (?, ?, ?)", alb.Title, alb.Artist, alb.Price)
    	if err != nil {
    		return 0, fmt.Errorf("addAlbum: %v", err)
    	}
    	id, err := result.LastInsertId()
    	if err != nil {
    		return 0, fmt.Errorf("addAlbum: %v", err)
    	}
    	return id, nil
    }
    ```

    Neste código, você:

    *   Usa [`DB.Exec`](https://pkg.go.dev/database/sql#DB.Exec) para
        executar uma instrução `INSERT`.

        Assim como `Query`, `Exec` recebe uma instrução SQL seguida dos valores
        dos parâmetros da instrução.

    *   Verifica se há erro na tentativa de `INSERT`.

    *   Obtém o ID da linha inserida no banco de dados usando
        [`Result.LastInsertId`](https://pkg.go.dev/database/sql#Result.LastInsertId).

    *   Verifica se há erro na tentativa de obter o ID.

2. Atualize `main` para chamar a nova função `addAlbum`.

    No final de `func main`, adicione o código a seguir.

    ```
    albID, err := addAlbum(Album{
    	Title:  "The Modern Sound of Betty Carter",
    	Artist: "Betty Carter",
    	Price:  49.99,
    })
    if err != nil {
    	log.Fatal(err)
    }
    fmt.Printf("ID of added album: %v\n", albID)
    ```

    No código novo, você agora:

    *   Chama `addAlbum` com um novo álbum, atribuindo o ID do álbum que você está
        adicionando a uma variável `albID`.

#### Executar o código

Na linha de comando, no diretório que contém o main.go, execute o código.

```
$ go run .
Connected!
Albums found: [{1 Blue Train John Coltrane 56.99} {2 Giant Steps John Coltrane 63.99}]
Album found: {2 Giant Steps John Coltrane 63.99}
ID of added album: 5
```

## Conclusão {#conclusion}

Parabéns! Você acabou de usar Go para executar ações simples com um banco de
dados relacional.

Próximos tópicos sugeridos:

*   Dê uma olhada no guia de acesso a dados, que inclui mais informações sobre
    os assuntos apenas tocados aqui.

*   Se você é novo em Go, vai encontrar boas práticas úteis descritas em
    [Effective Go](/doc/effective_go) e [Como escrever código Go](/doc/code).

*   O [Go Tour](/tour/) é uma ótima introdução passo a passo aos fundamentos do
    Go.

## Código completo {#completed_code}

Esta seção contém o código da aplicação que você constrói com este tutorial.

```
package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	"github.com/go-sql-driver/mysql"
)

var db *sql.DB

type Album struct {
	ID     int64
	Title  string
	Artist string
	Price  float32
}

func main() {
	// Capture connection properties.
	cfg := mysql.NewConfig()
	cfg.User = os.Getenv("DBUSER")
	cfg.Passwd = os.Getenv("DBPASS")
	cfg.Net = "tcp"
	cfg.Addr = "127.0.0.1:3306"
	cfg.DBName = "recordings"

	// Get a database handle.
	var err error
	db, err = sql.Open("mysql", cfg.FormatDSN())
	if err != nil {
		log.Fatal(err)
	}

	pingErr := db.Ping()
	if pingErr != nil {
		log.Fatal(pingErr)
	}
	fmt.Println("Connected!")

	albums, err := albumsByArtist("John Coltrane")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Albums found: %v\n", albums)

	// Hard-code ID 2 here to test the query.
	alb, err := albumByID(2)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Album found: %v\n", alb)

	albID, err := addAlbum(Album{
		Title:  "The Modern Sound of Betty Carter",
		Artist: "Betty Carter",
		Price:  49.99,
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("ID of added album: %v\n", albID)
}

// albumsByArtist queries for albums that have the specified artist name.
func albumsByArtist(name string) ([]Album, error) {
	// An albums slice to hold data from returned rows.
	var albums []Album

	rows, err := db.Query("SELECT * FROM album WHERE artist = ?", name)
	if err != nil {
		return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
	}
	defer rows.Close()
	// Loop through rows, using Scan to assign column data to struct fields.
	for rows.Next() {
		var alb Album
		if err := rows.Scan(&alb.ID, &alb.Title, &alb.Artist, &alb.Price); err != nil {
			return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
		}
		albums = append(albums, alb)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
	}
	return albums, nil
}

// albumByID queries for the album with the specified ID.
func albumByID(id int64) (Album, error) {
	// An album to hold data from the returned row.
	var alb Album

	row := db.QueryRow("SELECT * FROM album WHERE id = ?", id)
	if err := row.Scan(&alb.ID, &alb.Title, &alb.Artist, &alb.Price); err != nil {
		if err == sql.ErrNoRows {
			return alb, fmt.Errorf("albumsById %d: no such album", id)
		}
		return alb, fmt.Errorf("albumsById %d: %v", id, err)
	}
	return alb, nil
}

// addAlbum adds the specified album to the database,
// returning the album ID of the new entry
func addAlbum(alb Album) (int64, error) {
	result, err := db.Exec("INSERT INTO album (title, artist, price) VALUES (?, ?, ?)", alb.Title, alb.Artist, alb.Price)
	if err != nil {
		return 0, fmt.Errorf("addAlbum: %v", err)
	}
	id, err := result.LastInsertId()
	if err != nil {
		return 0, fmt.Errorf("addAlbum: %v", err)
	}
	return id, nil
}
```

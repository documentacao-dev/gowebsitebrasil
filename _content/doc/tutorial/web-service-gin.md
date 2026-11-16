<!--{
  "ia-translated": true,
  "Title": "Tutorial: Desenvolvendo uma API RESTful com Go e Gin",
  "Breadcrumb": true
}-->

Este tutorial apresenta o básico de como escrever uma API de serviço web RESTful com Go
e o [Gin Web Framework](https://gin-gonic.com/en/docs/) (Gin).

Você vai tirar o melhor proveito deste tutorial se já tiver familiaridade básica com Go
e suas ferramentas. Se este for seu primeiro contato com Go, veja
[Tutorial: Comece com Go](/doc/tutorial/getting-started) para uma introdução rápida.

O Gin simplifica muitas tarefas de programação associadas à criação de aplicações web,
incluindo serviços web. Neste tutorial, você vai usar o Gin para rotear requisições,
obter detalhes das requisições e serializar JSON para as respostas.

Neste tutorial, você vai criar um servidor de API RESTful com dois endpoints. O seu projeto
de exemplo será um repositório de dados sobre discos de jazz vintage.

O tutorial inclui as seguintes seções:

1. Projetar os endpoints da API.
2. Criar uma pasta para o seu código.
3. Criar os dados.
4. Escrever um handler para retornar todos os itens.
5. Escrever um handler para adicionar um novo item.
6. Escrever um handler para retornar um item específico.

**Observação:** para outros tutoriais, veja [Tutoriais](/doc/tutorial/index.html).

Para testar este tutorial como um tutorial interativo que você completa no Google Cloud Shell,
clique no botão abaixo.

[![Abrir no Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.png)](https://ide.cloud.google.com/?cloudshell_workspace=~&walkthrough_tutorial_url=https://raw.githubusercontent.com/golang/tour/master/tutorial/web-service-gin.md)


## Pré-requisitos

*   **Go.** Recomendamos usar a versão mais recente do Go para seguir este tutorial.
    Para as instruções de instalação, veja [Instalando o Go](/doc/install).
*   **Uma ferramenta para editar o seu código.** Qualquer editor de texto que você tenha vai funcionar bem.
*   **Um terminal de linha de comando.** O Go funciona bem em qualquer terminal no Linux e no Mac,
    e no PowerShell ou no cmd do Windows.
*   **A ferramenta curl.** No Linux e no Mac, ela normalmente já está instalada. No Windows, ela
    vem incluída no Windows 10 Insider build 17063 e posteriores. Para versões mais antigas do
    Windows, talvez seja necessário instalá-la. Para mais detalhes, veja
    [Tar e Curl chegam ao Windows](https://docs.microsoft.com/en-us/virtualization/community/team-blog/2017/20171219-tar-and-curl-come-to-windows).

## Projetar os endpoints da API {#design_endpoints}

Você vai criar uma API que dá acesso a uma loja que vende gravações vintage em vinil. Assim,
você precisará fornecer endpoints pelos quais um cliente possa obter e adicionar álbuns para os usuários.

Ao desenvolver uma API, normalmente você começa projetando os endpoints. Os usuários da sua API
terão mais sucesso se os endpoints forem fáceis de entender.

Estes são os endpoints que você vai criar neste tutorial.

/albums
*   `GET` – Obter uma lista de todos os álbuns, retornada como JSON.
*   `POST` – Adicionar um novo álbum a partir dos dados da requisição enviados como JSON.

/albums/:id
*   `GET` – Obter um álbum pelo seu ID, retornando os dados do álbum como JSON.

Em seguida, você vai criar uma pasta para o seu código.

## Criar uma pasta para o seu código {#create_folder}

Para começar, crie um projeto para o código que você vai escrever.

1. Abra um prompt de comando e mude para o seu diretório home.

    No Linux ou Mac:

    ```
    $ cd
    ```

    No Windows:

    ```
    C:\> cd %HOMEPATH%
    ```

2. No prompt de comando, crie um diretório para o seu código chamado
    web-service-gin.

    ```
    $ mkdir web-service-gin
    $ cd web-service-gin
    ```

3. Crie um módulo no qual você possa gerenciar dependências.

    Execute o comando `go mod init`, informando o caminho do módulo em que o seu código ficará.

    ```
    $ go mod init example/web-service-gin
    go: creating new go.mod: module example/web-service-gin
    ```

    Este comando cria um arquivo go.mod, no qual as dependências que você adicionar serão
    listadas para controle. Para saber mais sobre como nomear um módulo com um caminho de módulo, veja
    [Gerenciando dependências](/doc/modules/managing-dependencies#naming_module).

Em seguida, você vai projetar as estruturas de dados para lidar com os dados.

## Criar os dados {#create_data}

Para manter as coisas simples no tutorial, você vai armazenar os dados em memória. Uma API mais
típica interagiria com um banco de dados.

Observe que armazenar os dados em memória significa que o conjunto de álbuns será perdido sempre
que você parar o servidor, e recriado quando você o iniciar.

#### Escrever o código

1. Usando o seu editor de texto, crie um arquivo chamado main.go na pasta web-service-gin.
    Você vai escrever o seu código Go neste arquivo.
2. No main.go, no topo do arquivo, cole a seguinte declaração de pacote.

    ```
    package main
    ```

    Um programa independente (em oposição a uma biblioteca) sempre fica no pacote `main`.

3. Logo abaixo da declaração de pacote, cole a seguinte declaração da struct `album`. Você vai usá-la
    para armazenar os dados dos álbuns em memória.

    Tags de struct, como ``json:"artist"``, especificam qual deve ser o nome de um campo quando o
    conteúdo da struct é serializado em JSON. Sem elas, o JSON usaria os nomes dos campos com a inicial
    maiúscula, um estilo menos comum em JSON.

    ```
    // album represents data about a record album.
    type album struct {
    	ID     string  `json:"id"`
    	Title  string  `json:"title"`
    	Artist string  `json:"artist"`
    	Price  float64 `json:"price"`
    }
    ```

4. Logo abaixo da declaração de struct que você acabou de adicionar, cole o seguinte slice de structs
    `album`, com os dados que você vai usar para começar.

    ```
    // albums slice to seed record album data.
    var albums = []album{
    	{ID: "1", Title: "Blue Train", Artist: "John Coltrane", Price: 56.99},
    	{ID: "2", Title: "Jeru", Artist: "Gerry Mulligan", Price: 17.99},
    	{ID: "3", Title: "Sarah Vaughan and Clifford Brown", Artist: "Sarah Vaughan", Price: 39.99},
    }
    ```

Em seguida, você vai escrever o código para implementar o seu primeiro endpoint.

## Escrever um handler para retornar todos os itens {#all_items}

Quando o cliente fizer uma requisição em `GET /albums`, você quer retornar todos os álbuns como JSON.

Para isso, você vai escrever o seguinte:

*   Lógica para preparar a resposta
*   Código que mapeia o caminho da requisição para a sua lógica

Observe que essa é a ordem inversa da ordem de execução em tempo de execução, mas você está
adicionando as dependências primeiro e, depois, o código que depende delas.

#### Escrever o código

1. Logo abaixo do código da struct que você adicionou na seção anterior, cole o código a seguir para
    obter a lista de álbuns.

    A função `getAlbums` cria JSON a partir do slice de structs `album`, escrevendo o JSON na resposta.

    ```
    // getAlbums responds with the list of all albums as JSON.
    func getAlbums(c *gin.Context) {
    	c.IndentedJSON(http.StatusOK, albums)
    }
    ```

    Neste código, você:

    *   Escreve uma função `getAlbums` que recebe um parâmetro
        [`gin.Context`](https://pkg.go.dev/github.com/gin-gonic/gin#Context). Observe que você poderia ter
        dado a esta função qualquer nome: nem o Gin nem o Go exigem um formato específico de nome de função.

        `gin.Context` é a parte mais importante do Gin. Ele carrega os detalhes da requisição, valida e
        serializa JSON, entre outras coisas. (Apesar do nome parecido, isso é diferente do pacote embutido
        [`context`](/pkg/context/) do Go.)

    *   Chama [`Context.IndentedJSON`](https://pkg.go.dev/github.com/gin-gonic/gin#Context.IndentedJSON)
        para serializar a struct em JSON e adicioná-la à resposta.

        O primeiro argumento da função é o código de status HTTP que você quer enviar ao cliente. Aqui,
        você está passando a constante [`StatusOK`](https://pkg.go.dev/net/http#StatusOK), do pacote
        `net/http`, para indicar `200 OK`.

        Observe que você pode substituir `Context.IndentedJSON` por uma chamada a
        [`Context.JSON`](https://pkg.go.dev/github.com/gin-gonic/gin#Context.JSON) para enviar um JSON mais
        compacto. Na prática, a forma indentada é muito mais fácil de trabalhar ao depurar, e a diferença
        de tamanho costuma ser pequena.

2. Perto do topo do main.go, logo abaixo da declaração do slice `albums`, cole o código abaixo para
    associar a função handler a um caminho de endpoint.

    Isso estabelece uma associação em que `getAlbums` trata as requisições ao caminho de endpoint
    `/albums`.

    ```
    func main() {
    	router := gin.Default()
    	router.GET("/albums", getAlbums)

    	router.Run("localhost:8080")
    }
    ```

    Neste código, você:

    *   Inicializa um roteador Gin usando [`Default`](https://pkg.go.dev/github.com/gin-gonic/gin#Default).
    *   Usa a função [`GET`](https://pkg.go.dev/github.com/gin-gonic/gin#RouterGroup.GET) para associar o
        método HTTP `GET` e o caminho `/albums` a uma função handler.

        Observe que você está passando o _nome_ da função `getAlbums`. Isso é diferente de passar o
        _resultado_ da função, o que você faria passando `getAlbums()` (note os parênteses).

    *   Usa a função [`Run`](https://pkg.go.dev/github.com/gin-gonic/gin#Engine.Run) para anexar o
        roteador a um `http.Server` e iniciar o servidor.

3. Perto do topo do main.go, logo abaixo da declaração de pacote, importe os pacotes de que você vai
    precisar para dar suporte ao código que acabou de escrever.

    As primeiras linhas do código devem ficar assim:

    ```
    package main

    import (
    	"net/http"

    	"github.com/gin-gonic/gin"
    )
    ```

4. Salve o main.go.

#### Executar o código

1. Comece a rastrear o módulo Gin como dependência.

    Na linha de comando, use [`go get`](/cmd/go/#hdr-Add_dependencies_to_current_module_and_install_them)
    para adicionar o módulo github.com/gin-gonic/gin como dependência do seu módulo. Use um argumento de
    ponto para indicar “obter as dependências do código no diretório atual”.

    ```
    $ go get .
    go get: added github.com/gin-gonic/gin v1.7.2
    ```

    O Go resolveu e baixou essa dependência para satisfazer a declaração `import` que você adicionou na
    etapa anterior.

2. Na linha de comando, no diretório que contém o main.go, execute o código. Use um argumento de ponto
    para indicar “executar o código no diretório atual”.

    ```
    $ go run .
    ```

    Com o código em execução, você tem um servidor HTTP ativo para o qual pode enviar requisições.

3. Em uma nova janela de linha de comando, use `curl` para fazer uma requisição ao seu serviço web em execução.

    ```
    $ curl http://localhost:8080/albums
    ```

    O comando deve exibir os dados com que você populou o serviço.

    ```
    [
            {
                    "id": "1",
                    "title": "Blue Train",
                    "artist": "John Coltrane",
                    "price": 56.99
            },
            {
                    "id": "2",
                    "title": "Jeru",
                    "artist": "Gerry Mulligan",
                    "price": 17.99
            },
            {
                    "id": "3",
                    "title": "Sarah Vaughan and Clifford Brown",
                    "artist": "Sarah Vaughan",
                    "price": 39.99
            }
    ]
    ```

Você iniciou uma API! Na próxima seção, você vai criar outro endpoint, com código para tratar uma
requisição `POST` que adiciona um item.

## Escrever um handler para adicionar um novo item {#add_item}

Quando o cliente fizer uma requisição `POST` em `/albums`, você quer adicionar o álbum descrito no corpo da requisição aos dados de álbuns existentes.

Para isso, você vai escrever o seguinte:

*   Lógica para adicionar o novo álbum à lista existente.
*   Um pouco de código para direcionar a requisição `POST` para a sua lógica.

#### Escrever o código

1. Adicione código para incluir os dados de álbuns na lista de álbuns.

    Em algum lugar depois das declarações `import`, cole o código a seguir. (O final do arquivo é um bom
    lugar para esse código, mas o Go não exige uma ordem para declarar funções.)

    ```
    // postAlbums adds an album from JSON received in the request body.
    func postAlbums(c *gin.Context) {
    	var newAlbum album

    	// Call BindJSON to bind the received JSON to
    	// newAlbum.
    	if err := c.BindJSON(&newAlbum); err != nil {
    		return
    	}

    	// Add the new album to the slice.
    	albums = append(albums, newAlbum)
    	c.IndentedJSON(http.StatusCreated, newAlbum)
    }
    ```

    Neste código, você:

    *   Usa [`Context.BindJSON`](https://pkg.go.dev/github.com/gin-gonic/gin#Context.BindJSON) para vincular
        o corpo da requisição a `newAlbum`.
    *   Adiciona a struct `album` inicializada a partir do JSON ao slice `albums`.
    *   Adiciona um código de status `201` à resposta, junto com o JSON que representa o álbum adicionado.

2. Altere a função `main` para incluir a chamada a `router.POST`, como no exemplo a seguir.

    ```
    func main() {
    	router := gin.Default()
    	router.GET("/albums", getAlbums)
    	router.POST("/albums", postAlbums)

    	router.Run("localhost:8080")
    }
    ```

    Neste código, você:

    *   Associa o método `POST` no caminho `/albums` à função `postAlbums`.

        Com o Gin, você pode associar um handler a uma combinação de método HTTP e caminho. Assim, você
        pode rotear separadamente as requisições enviadas a um mesmo caminho conforme o método que o cliente
        está usando.

#### Executar o código

1. Se o servidor ainda estiver em execução da seção anterior, pare-o.
2. Na linha de comando, no diretório que contém o main.go, execute o código.

    ```
    $ go run .
    ```

3. Em outra janela de linha de comando, use `curl` para fazer uma requisição ao seu serviço web em execução.

    ```
    $ curl http://localhost:8080/albums \
        --include \
        --header "Content-Type: application/json" \
        --request "POST" \
        --data '{"id": "4","title": "The Modern Sound of Betty Carter","artist": "Betty Carter","price": 49.99}'
    ```

    O comando deve exibir os cabeçalhos e o JSON do álbum adicionado.

    ```
    HTTP/1.1 201 Created
    Content-Type: application/json; charset=utf-8
    Date: Wed, 02 Jun 2021 00:34:12 GMT
    Content-Length: 116

    {
        "id": "4",
        "title": "The Modern Sound of Betty Carter",
        "artist": "Betty Carter",
        "price": 49.99
    }
    ```

4. Como na seção anterior, use `curl` para obter a lista completa de álbuns, o que permite confirmar que o novo álbum foi adicionado.

    ```
    $ curl http://localhost:8080/albums \
        --header "Content-Type: application/json" \
        --request "GET"
    ```

    O comando deve exibir a lista de álbuns.

    ```
    [
            {
                    "id": "1",
                    "title": "Blue Train",
                    "artist": "John Coltrane",
                    "price": 56.99
            },
            {
                    "id": "2",
                    "title": "Jeru",
                    "artist": "Gerry Mulligan",
                    "price": 17.99
            },
            {
                    "id": "3",
                    "title": "Sarah Vaughan and Clifford Brown",
                    "artist": "Sarah Vaughan",
                    "price": 39.99
            },
            {
                    "id": "4",
                    "title": "The Modern Sound of Betty Carter",
                    "artist": "Betty Carter",
                    "price": 49.99
            }
    ]
    ```

Na próxima seção, você vai adicionar código para tratar um `GET` de um item específico.

## Escrever um handler para retornar um item específico {#specific_item}

Quando o cliente fizer uma requisição em `GET /albums/[id]`, você quer retornar o álbum cujo ID
corresponde ao parâmetro de caminho `id`.

Para isso, você vai:

*   Adicionar lógica para buscar o álbum solicitado.
*   Mapear o caminho para a lógica.

#### Escrever o código

1. Logo abaixo da função `postAlbums` que você adicionou na seção anterior, cole o código a seguir para
    buscar um álbum específico.

    Esta função `getAlbumByID` vai extrair o ID presente no caminho da requisição e, em seguida,
    localizar o álbum correspondente.

    ```
    // getAlbumByID locates the album whose ID value matches the id
    // parameter sent by the client, then returns that album as a response.
    func getAlbumByID(c *gin.Context) {
    	id := c.Param("id")

    	// Loop over the list of albums, looking for
    	// an album whose ID value matches the parameter.
    	for _, a := range albums {
    		if a.ID == id {
    			c.IndentedJSON(http.StatusOK, a)
    			return
    		}
    	}
    	c.IndentedJSON(http.StatusNotFound, gin.H{"message": "album not found"})
    }
    ```

    Neste código, você:

    *   Usa [`Context.Param`](https://pkg.go.dev/github.com/gin-gonic/gin#Context.Param) para obter o
        parâmetro de caminho `id` da URL. Ao mapear este handler para um caminho, você vai incluir um
        marcador para o parâmetro nesse caminho.
    *   Percorre as structs `album` do slice, procurando uma cujo campo `ID` tenha o mesmo valor do
        parâmetro `id`. Se ela for encontrada, serializa essa struct `album` em JSON e a retorna como
        resposta com o código HTTP `200 OK`.

        Como mencionado acima, um serviço do mundo real provavelmente usaria uma consulta a banco de dados
        para fazer essa busca.

    *   Retorna um erro HTTP `404` com [`http.StatusNotFound`](https://pkg.go.dev/net/http#StatusNotFound)
        se o álbum não for encontrado.

2. Por fim, altere o `main` para incluir uma nova chamada a `router.GET`, em que o caminho agora é
    `/albums/:id`, como mostrado no exemplo a seguir.

    ```
    func main() {
    	router := gin.Default()
    	router.GET("/albums", getAlbums)
    	router.GET("/albums/:id", getAlbumByID)
    	router.POST("/albums", postAlbums)

    	router.Run("localhost:8080")
    }
    ```

    Neste código, você:

    *   Associa o caminho `/albums/:id` à função `getAlbumByID`. No Gin, os dois-pontos antes de um item
        do caminho indicam que esse item é um parâmetro de caminho.

#### Executar o código

1. Se o servidor ainda estiver em execução da seção anterior, pare-o.
2. Na linha de comando, no diretório que contém o main.go, execute o código para iniciar o servidor.

    ```
    $ go run .
    ```

3. Em outra janela de linha de comando, use `curl` para fazer uma requisição ao seu serviço web em execução.

    ```
    $ curl http://localhost:8080/albums/2
    ```

    O comando deve exibir o JSON do álbum cujo ID você usou. Se o álbum não for encontrado, você verá
    um JSON com uma mensagem de erro.

    ```
    {
            "id": "2",
            "title": "Jeru",
            "artist": "Gerry Mulligan",
            "price": 17.99
    }
    ```

## Conclusão {#conclusion}

Parabéns! Você acaba de usar Go e Gin para escrever um serviço web RESTful simples.

Próximos tópicos sugeridos:

*   Se você é novo em Go, vai encontrar boas práticas úteis descritas em [Effective Go](/doc/effective_go)
    e [Como escrever código Go](/doc/code).
*   O [Go Tour](/tour/) é uma ótima introdução passo a passo aos fundamentos do Go.
*   Para saber mais sobre o Gin, veja a
    [documentação do pacote Gin Web Framework](https://pkg.go.dev/github.com/gin-gonic/gin)
    ou a [documentação do Gin Web Framework](https://gin-gonic.com/en/docs/).

## Código completo {#completed_code}

Esta seção contém o código da aplicação que você construiu neste tutorial.

```
package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// album represents data about a record album.
type album struct {
	ID     string  `json:"id"`
	Title  string  `json:"title"`
	Artist string  `json:"artist"`
	Price  float64 `json:"price"`
}

// albums slice to seed record album data.
var albums = []album{
	{ID: "1", Title: "Blue Train", Artist: "John Coltrane", Price: 56.99},
	{ID: "2", Title: "Jeru", Artist: "Gerry Mulligan", Price: 17.99},
	{ID: "3", Title: "Sarah Vaughan and Clifford Brown", Artist: "Sarah Vaughan", Price: 39.99},
}

func main() {
	router := gin.Default()
	router.GET("/albums", getAlbums)
	router.GET("/albums/:id", getAlbumByID)
	router.POST("/albums", postAlbums)

	router.Run("localhost:8080")
}

// getAlbums responds with the list of all albums as JSON.
func getAlbums(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, albums)
}

// postAlbums adds an album from JSON received in the request body.
func postAlbums(c *gin.Context) {
	var newAlbum album

	// Call BindJSON to bind the received JSON to
	// newAlbum.
	if err := c.BindJSON(&newAlbum); err != nil {
		return
	}

	// Add the new album to the slice.
	albums = append(albums, newAlbum)
	c.IndentedJSON(http.StatusCreated, newAlbum)
}

// getAlbumByID locates the album whose ID value matches the id
// parameter sent by the client, then returns that album as a response.
func getAlbumByID(c *gin.Context) {
	id := c.Param("id")

	// Loop through the list of albums, looking for
	// an album whose ID value matches the parameter.
	for _, a := range albums {
		if a.ID == id {
			c.IndentedJSON(http.StatusOK, a)
			return
		}
	}
	c.IndentedJSON(http.StatusNotFound, gin.H{"message": "album not found"})
}
```

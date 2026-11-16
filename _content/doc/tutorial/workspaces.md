<!--{
  "ia-translated": true,
  "Title": "Tutorial: Primeiros passos com workspaces de múltiplos módulos",
  "Breadcrumb": true
}-->

Este tutorial apresenta o básico dos workspaces de múltiplos módulos em Go.
Com os workspaces de múltiplos módulos, você pode informar ao comando go que está
escrevendo código em vários módulos ao mesmo tempo, e compilar e executar código
desses módulos com facilidade.

Neste tutorial, você vai criar dois módulos em um workspace compartilhado com
vários módulos, fazer alterações entre esses módulos e ver o resultado dessas
alterações em uma compilação.

<!-- TODO TOC -->

**Observação:** para outros tutoriais, veja [Tutoriais](/doc/tutorial/index.html).

## Pré-requisitos

*   **Go.** Recomendamos usar a versão mais recente do Go para seguir este tutorial.
    Para as instruções de instalação, veja [Instalando o Go](/doc/install).
*   **Uma ferramenta para editar o seu código.** Qualquer editor de texto que você
    tenha vai funcionar bem.
*   **Um terminal de linha de comando.** O Go funciona bem em qualquer terminal no
    Linux e no Mac, e no PowerShell ou no cmd do Windows.

## Criar um módulo para o seu código {#create_folder}

Para começar, crie um módulo para o código que você vai escrever.

1. Abra um prompt de comando e mude para o seu diretório home.

   No Linux ou Mac:

    ```
    $ cd
    ```

   No Windows:

    ```
    C:\> cd %HOMEPATH%
    ```

   O restante do tutorial vai mostrar um $ como prompt. Os comandos que você
   usar também vão funcionar no Windows.

2. No prompt de comando, crie um diretório para o seu código chamado workspace.

    ```
    $ mkdir workspace
    $ cd workspace
    ```

3. Inicialize o módulo

   O nosso exemplo vai criar um novo módulo `hello` que vai depender do módulo golang.org/x/example.

   Crie o módulo hello:

   ```
   $ mkdir hello
   $ cd hello
   $ go mod init example.com/hello
   go: creating new go.mod: module example.com/hello
   ```

   Adicione uma dependência do pacote golang.org/x/example/hello/reverse usando `go get`.

   ```
   $ go get golang.org/x/example/hello/reverse
   ```

   Crie o arquivo hello.go no diretório hello com o seguinte conteúdo:

   ```
   package main

   import (
       "fmt"

       "golang.org/x/example/hello/reverse"
   )

   func main() {
       fmt.Println(reverse.String("Hello"))
   }
   ```

   Agora, execute o programa hello:

   ```
   $ go run .
   olleH
   ```

## Criar o workspace

Nesta etapa, vamos criar um arquivo `go.work` para especificar um workspace com o módulo.

#### Inicializar o workspace

No diretório `workspace`, execute:

   ```
   $ go work init ./hello
   ```

O comando `go work init` instrui o `go` a criar um arquivo `go.work`
para um workspace que contém os módulos no diretório `./hello`.

O comando `go` gera um arquivo `go.work` com este conteúdo:

   ```
   go 1.18

   use ./hello
   ```

O arquivo `go.work` tem uma sintaxe semelhante à do `go.mod`.

A diretiva `go` informa ao Go com qual versão da linguagem o arquivo deve ser
interpretado. É semelhante à diretiva `go` do arquivo `go.mod`.

A diretiva `use` informa ao Go que o módulo no diretório `hello` deve ser tratado
como módulo principal durante a compilação.

Assim, em qualquer subdiretório de `workspace`, o módulo estará ativo.

#### Executar o programa no diretório do workspace

No diretório `workspace`, execute:

   ```
   $ go run ./hello
   olleH
   ```

O comando Go inclui todos os módulos do workspace como módulos principais. Isso
nos permite referenciar um pacote do módulo mesmo de fora dele. Executar o comando
`go run` fora do módulo ou do workspace resultaria em erro, porque o comando `go`
não saberia quais módulos usar.

Em seguida, vamos adicionar uma cópia local do módulo `golang.org/x/example/hello` ao
workspace. Esse módulo fica armazenado em um subdiretório do repositório Git
`go.googlesource.com/example`. Depois, vamos adicionar uma nova função ao pacote
`reverse` que podemos usar no lugar de `String`.

## Baixar e modificar o módulo `golang.org/x/example/hello`

   Nesta etapa, vamos baixar uma cópia do repositório Git que contém o módulo
   `golang.org/x/example/hello`, adicioná-la ao workspace e, em seguida, adicionar
   a ela uma nova função que vamos usar no programa hello.

1. Clone o repositório

   No diretório workspace, execute o comando `git` para clonar o repositório:

   ```
   $ git clone https://go.googlesource.com/example
   Cloning into 'example'...
   remote: Total 165 (delta 27), reused 165 (delta 27)
   Receiving objects: 100% (165/165), 434.18 KiB | 1022.00 KiB/s, done.
   Resolving deltas: 100% (27/27), done.
   ```

2. Adicione o módulo ao workspace

   O repositório Git acabou de ser copiado para `./example`.
   O código-fonte do módulo `golang.org/x/example/hello` está em `./example/hello`.
   Adicione-o ao workspace:

   ```
   $ go work use ./example/hello
   ```

   O comando `go work use` adiciona um novo módulo ao arquivo go.work. Agora ele
   fica assim:

   ```
   go 1.18

   use (
       ./hello
       ./example/hello
   )
   ```

   O workspace agora inclui tanto o módulo `example.com/hello` quanto o módulo
   `golang.org/x/example/hello`, que fornece o pacote `golang.org/x/example/hello/reverse`.

   Isso vai nos permitir usar o novo código que vamos escrever na nossa cópia do
   pacote `reverse`, em vez da versão do pacote que está no cache de módulos e que
   baixamos com o comando `go get`.

3. Adicione a nova função.

   Vamos adicionar ao pacote `golang.org/x/example/hello/reverse` uma nova função
   para inverter um número.

   Crie um novo arquivo chamado `int.go` no diretório `workspace/example/hello/reverse`
   com o seguinte conteúdo:

   ```
   package reverse

   import "strconv"

   // Int returns the decimal reversal of the integer i.
   func Int(i int) int {
       i, _ = strconv.Atoi(String(strconv.Itoa(i)))
       return i
   }
   ```

4. Modifique o programa hello para usar a função.

   Altere o conteúdo de `workspace/hello/hello.go` para que fique assim:

   ```
   package main

   import (
       "fmt"

       "golang.org/x/example/hello/reverse"
   )

   func main() {
       fmt.Println(reverse.String("Hello"), reverse.Int(24601))
   }
   ```

#### Executar o código no workspace

   No diretório workspace, execute

   ```
   $ go run ./hello
   olleH 10642
   ```

   O comando Go encontra o módulo `example.com/hello` especificado na linha de
   comando, no diretório `hello` indicado pelo arquivo `go.work`, e resolve de
   forma semelhante o import `golang.org/x/example/hello/reverse` usando o
   arquivo `go.work`.

   O `go.work` pode ser usado no lugar de adicionar diretivas
   [`replace`](/ref/mod#go-mod-file-replace) para trabalhar com vários módulos.

   Como os dois módulos estão no mesmo workspace, é fácil fazer uma alteração em
   um módulo e usá-la em outro.

#### Próximo passo

   Agora, para publicar esses módulos de forma adequada, precisaríamos lançar uma
   versão do módulo `golang.org/x/example/hello`, por exemplo a `v0.1.0`. Isso
   normalmente é feito marcando um commit no repositório de controle de versão do
   módulo. Veja a
   [documentação do fluxo de lançamento de módulos](/doc/modules/release-workflow)
   para mais detalhes. Depois do lançamento, podemos aumentar a exigência do módulo
   `golang.org/x/example/hello` em `hello/go.mod`:

   ```
   cd hello
   go get golang.org/x/example/hello@v0.1.0
   ```

   Assim, o comando `go` consegue resolver corretamente os módulos fora do workspace.

## Saiba mais sobre workspaces

   O comando `go` tem alguns subcomandos para trabalhar com workspaces, além do
   `go work init` que vimos antes neste tutorial:

   - `go work use [-r] [dir]` adiciona uma diretiva `use` ao arquivo `go.work` para
   `dir`, se ele existir, e remove a diretiva `use` se o diretório informado não
   existir. A flag `-r` examina os subdiretórios de `dir` recursivamente.
   - `go work edit` edita o arquivo `go.work` de forma semelhante ao `go mod edit`.
   - `go work sync` sincroniza as dependências da lista de compilação do workspace
   com cada um dos módulos do workspace.

   Veja [Workspaces](/ref/mod#workspaces) na Referência de Módulos do Go para mais
   detalhes sobre workspaces e arquivos `go.work`.

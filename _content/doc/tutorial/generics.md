<!--{
  "ia-translated": true,
  "Title": "Tutorial: Primeiros passos com generics",
  "Breadcrumb": true
}-->

Este tutorial apresenta o básico de generics em Go. Com generics, você pode
declarar e usar funções ou tipos escritos para funcionar com qualquer um de um
conjunto de tipos fornecidos pelo código que faz a chamada.

Neste tutorial, você vai declarar duas funções simples sem generics e, em seguida,
capturar a mesma lógica em uma única função genérica.

Você vai avançar pelas seguintes seções:

1. Criar uma pasta para o seu código.
2. Adicionar funções sem generics.
3. Adicionar uma função genérica para tratar vários tipos.
4. Remover os argumentos de tipo ao chamar a função genérica.
5. Declarar uma restrição de tipo.

**Observação:** Para outros tutoriais, veja [Tutoriais](/doc/tutorial/index.html).

## Pré-requisitos

*   **Go.** Recomendamos usar a versão mais recente do Go para acompanhar este tutorial.
    Para instruções de instalação, veja [Instalando o Go](/doc/install).
*   **Uma ferramenta para editar seu código.** Qualquer editor de texto que você tenha
    funciona bem.
*   **Um terminal de comandos.** O Go funciona bem em qualquer terminal no Linux e no Mac,
    e no PowerShell ou cmd no Windows.

## Criar uma pasta para o seu código {#create_folder}

Para começar, crie uma pasta para o código que você vai escrever.

1. Abra um prompt de comando e vá para o seu diretório pessoal.

    No Linux ou Mac:

    ```
    $ cd
    ```

    No Windows:

    ```
    C:\> cd %HOMEPATH%
    ```

    O restante do tutorial vai mostrar um $ como prompt. Os comandos que você usar
    também vão funcionar no Windows.

2. No prompt de comando, crie um diretório para o seu código chamado generics.

    ```
    $ mkdir generics
    $ cd generics
    ```

3. Crie um módulo para guardar o seu código.

    Execute o comando `go mod init`, passando o caminho do módulo do seu novo código.

    ```
    $ go mod init example/generics
    go: creating new go.mod: module example/generics
    ```

    **Observação:** Para código de produção, você especificaria um caminho de módulo mais específico
    para as suas necessidades. Para saber mais, não deixe de ver
    [Gerenciando dependências](/doc/modules/managing-dependencies).

Em seguida, você vai adicionar um código simples para trabalhar com maps.

## Adicionar funções sem generics {#non_generic_functions}

Nesta etapa, você vai adicionar duas funções que, cada uma, somam os valores de um
map e retornam o total.

Você está declarando duas funções em vez de uma porque está trabalhando com dois
tipos diferentes de maps: um que armazena valores `int64` e outro que armazena valores `float64`.

#### Escreva o código

1. Usando o seu editor de texto, crie um arquivo chamado main.go no diretório
    generics. É neste arquivo que você vai escrever o seu código Go.
2. No main.go, no topo do arquivo, cole a seguinte
    declaração de pacote.

    ```
    package main
    ```

    Um programa independente (em oposição a uma biblioteca) sempre fica no pacote `main`.

3. Abaixo da declaração de pacote, cole as duas declarações de função a seguir.

    ```
    // SumInts adds together the values of m.
    func SumInts(m map[string]int64) int64 {
    	var s int64
    	for _, v := range m {
    		s += v
    	}
    	return s
    }

    // SumFloats adds together the values of m.
    func SumFloats(m map[string]float64) float64 {
    	var s float64
    	for _, v := range m {
    		s += v
    	}
    	return s
    }
    ```

    Neste código, você:

    *   Declara duas funções para somar os valores de um map e retornar
        a soma.
        *   `SumFloats` recebe um map de valores `string` para `float64`.
        *   `SumInts` recebe um map de valores `string` para `int64`.

4. No topo do main.go, abaixo da declaração de pacote, cole a seguinte
    função `main` para inicializar os dois maps e usá-los como argumentos ao chamar as
    funções que você declarou na etapa anterior.

    ```
    func main() {
    	// Initialize a map for the integer values
    	ints := map[string]int64{
    		"first":  34,
    		"second": 12,
    	}

    	// Initialize a map for the float values
    	floats := map[string]float64{
    		"first":  35.98,
    		"second": 26.99,
    	}

    	fmt.Printf("Non-Generic Sums: %v and %v\n",
    		SumInts(ints),
    		SumFloats(floats))
    }
    ```

    Neste código, você:

    *   Inicializa um map de valores `float64` e um map de valores `int64`, cada
        um com duas entradas.
    *   Chama as duas funções que você declarou antes para encontrar a soma dos
        valores de cada map.
    *   Imprime o resultado.

5. No topo do main.go, logo abaixo da declaração de pacote, importe o
    pacote de que você vai precisar para dar suporte ao código que acabou de escrever.

    As primeiras linhas de código devem ficar assim:

    ```
    package main

    import "fmt"
    ```

6. Salve o main.go.

#### Execute o código

Na linha de comando, no diretório que contém o main.go, execute o código.

```
$ go run .
Non-Generic Sums: 46 and 62.97
```

Com generics, você pode escrever uma função aqui em vez de duas. Em seguida, você vai
adicionar uma única função genérica para maps que contêm valores inteiros ou float.

## Adicionar uma função genérica para tratar vários tipos {#add_generic_function}

Nesta seção, você vai adicionar uma única função genérica que pode receber um map
contendo valores inteiros ou float, substituindo efetivamente as duas
funções que você acabou de escrever por uma única função.

Para dar suporte a valores de qualquer um dos tipos, essa função única vai precisar de uma
forma de declarar quais tipos ela suporta. Já o código que faz a chamada vai precisar de uma
forma de especificar se está chamando com um map de inteiros ou de float.

Para isso, você vai escrever uma função que declara _parâmetros de tipo_ além de
seus parâmetros de função comuns. Esses parâmetros de tipo tornam a
função genérica, permitindo que ela funcione com argumentos de tipos diferentes. Você vai
chamar a função com _argumentos de tipo_ e argumentos de função comuns.

Cada parâmetro de tipo tem uma _restrição de tipo_ que atua como uma espécie de
meta-tipo para o parâmetro de tipo. Cada restrição de tipo especifica os argumentos de tipo
permitidos que o código que faz a chamada pode usar para o respectivo parâmetro de tipo.

Embora a restrição de um parâmetro de tipo normalmente represente um conjunto de tipos, em tempo
de compilação o parâmetro de tipo representa um único tipo – o tipo fornecido
como argumento de tipo pelo código que faz a chamada. Se o tipo do argumento de tipo
não for permitido pela restrição do parâmetro de tipo, o código não será compilado.

Lembre-se de que um parâmetro de tipo precisa suportar todas as operações que o código genérico
executa sobre ele. Por exemplo, se o código da sua função tentasse
executar operações de `string` (como indexação) em um parâmetro de tipo cuja restrição incluísse
tipos numéricos, o código não compilaria.

No código que você está prestes a escrever, você vai usar uma restrição que permite
tipos inteiros ou float.

#### Escreva o código

1. Abaixo das duas funções que você adicionou antes, cole a seguinte função
    genérica.

    ```
    // SumIntsOrFloats sums the values of map m. It supports both int64 and float64
    // as types for map values.
    func SumIntsOrFloats[K comparable, V int64 | float64](m map[K]V) V {
        var s V
        for _, v := range m {
            s += v
        }
        return s
    }
    ```

    Neste código, você:

    *   Declara uma função `SumIntsOrFloats` com dois parâmetros de tipo (dentro
        dos colchetes), `K` e `V`, e um argumento que usa os parâmetros de tipo,
        `m` do tipo `map[K]V`. A função retorna um valor do
        tipo `V`.
    *   Especifica para o parâmetro de tipo `K` a restrição `comparable`.
        Pensada especificamente para casos como este, a restrição `comparable`
        é pré-declarada em Go. Ela permite qualquer tipo cujos valores possam ser usados como
        operando dos operadores de comparação `==` e `!=`. O Go exige que as chaves de
        map sejam comparáveis. Por isso, declarar `K` como `comparable` é necessário para que você possa
        usar `K` como chave na variável map. Isso também garante que o código que faz a
        chamada use um tipo permitido para chaves de map.
    *   Especifica para o parâmetro de tipo `V` uma restrição que é uma união de dois
        tipos: `int64` e `float64`. Usar `|` especifica uma união dos dois
        tipos, o que significa que essa restrição permite qualquer um dos tipos. Qualquer um dos
        tipos será aceito pelo compilador como argumento no código que faz a chamada.
    *   Especifica que o argumento `m` é do tipo `map[K]V`, em que `K` e `V`
        são os tipos já especificados para os parâmetros de tipo. Observe que sabemos que
        `map[K]V` é um tipo de map válido porque `K` é um tipo comparável. Se
        não tivéssemos declarado `K` como comparable, o compilador rejeitaria a
        referência a `map[K]V`.

2. No main.go, abaixo do código que você já tem, cole o seguinte código.

    ```
    fmt.Printf("Generic Sums: %v and %v\n",
    	SumIntsOrFloats[string, int64](ints),
    	SumIntsOrFloats[string, float64](floats))
    ```

    Neste código, você:

    *   Chama a função genérica que você acabou de declarar, passando cada um dos maps
        que você criou.
    *   Especifica argumentos de tipo – os nomes de tipo entre colchetes – para deixar
        claro quais tipos devem substituir os parâmetros de tipo na
        função que você está chamando.

        Como você vai ver na próxima seção, muitas vezes você pode omitir os
        argumentos de tipo na chamada da função. O Go consegue inferi-los a partir do seu
        código com frequência.
    *   Imprime as somas retornadas pela função.

#### Execute o código

Na linha de comando, no diretório que contém o main.go, execute o código.

```
$ go run .
Non-Generic Sums: 46 and 62.97
Generic Sums: 46 and 62.97
```

Para executar o seu código, em cada chamada o compilador substituiu os parâmetros de tipo
pelos tipos concretos especificados naquela chamada.

Ao chamar a função genérica que você escreveu, você especificou argumentos de tipo que
informaram ao compilador quais tipos usar no lugar dos parâmetros de tipo da função.
Como você vai ver na próxima seção, em muitos casos você pode omitir esses
argumentos de tipo, porque o compilador consegue inferi-los.

## Remover os argumentos de tipo ao chamar a função genérica {#remove_type_arguments}

Nesta seção, você vai adicionar uma versão modificada da chamada da função genérica,
fazendo uma pequena alteração para simplificar o código de chamada. Você vai
remover os argumentos de tipo, que não são necessários neste caso.

Você pode omitir argumentos de tipo no código que faz a chamada quando o compilador do Go consegue
inferir os tipos que você quer usar. O compilador infere os argumentos de tipo a partir dos
tipos dos argumentos da função.

Observe que nem sempre isso é possível. Por exemplo, se você precisasse chamar uma
função genérica que não tem argumentos, teria de incluir os argumentos de tipo
na chamada da função.

#### Escreva o código

*   No main.go, abaixo do código que você já tem, cole o seguinte código.

    ```
    fmt.Printf("Generic Sums, type parameters inferred: %v and %v\n",
    	SumIntsOrFloats(ints),
    	SumIntsOrFloats(floats))
    ```

    Neste código, você:

    *   Chama a função genérica, omitindo os argumentos de tipo.

#### Execute o código

Na linha de comando, no diretório que contém o main.go, execute o código.

```
$ go run .
Non-Generic Sums: 46 and 62.97
Generic Sums: 46 and 62.97
Generic Sums, type parameters inferred: 46 and 62.97
```

Em seguida, você vai simplificar ainda mais a função, capturando a união de inteiros
e float em uma restrição de tipo que você pode reutilizar, por exemplo, em outro código.

## Declarar uma restrição de tipo {#declare_type_constraint}

Na última seção, você vai mover a restrição que definiu antes para
sua própria interface, para poder reutilizá-la em vários lugares. Declarar
restrições dessa forma ajuda a deixar o código mais enxuto, principalmente quando a restrição é
mais complexa.

Você declara uma _restrição de tipo_ como uma interface. A restrição permite qualquer
tipo que implemente a interface. Por exemplo, se você declarar uma interface de restrição de tipo
com três métodos e, em seguida, usá-la com um parâmetro de tipo em uma
função genérica, os argumentos de tipo usados para chamar a função precisam ter todos esses
métodos.

Interfaces de restrição também podem se referir a tipos específicos, como você vai ver
nesta seção.

#### Escreva o código

1. Logo acima de `main`, imediatamente após as instruções de import, cole o
    código a seguir para declarar uma restrição de tipo.

    ```
    type Number interface {
        int64 | float64
    }
    ```

    Neste código, você:

    *   Declara o tipo de interface `Number` para usar como restrição de tipo.
    *   Declara uma união de `int64` e `float64` dentro da interface.

        Essencialmente, você está movendo a união da declaração da função
        para uma nova restrição de tipo. Assim, quando quiser restringir um parâmetro de tipo a
        `int64` ou `float64`, pode usar esta restrição de tipo `Number`
        em vez de escrever `int64 | float64`.

2. Abaixo das funções que você já tem, cole a seguinte função genérica
    `SumNumbers`.

    ```
    // SumNumbers sums the values of map m. It supports both integers
    // and floats as map values.
    func SumNumbers[K comparable, V Number](m map[K]V) V {
        var s V
        for _, v := range m {
            s += v
        }
        return s
    }
    ```

    Neste código, você:

    *   Declara uma função genérica com a mesma lógica da função genérica
        que você declarou antes, mas com o novo tipo de interface no lugar da união
        como restrição de tipo. Como antes, você usa os parâmetros de tipo
        nos tipos dos argumentos e do retorno.

3. No main.go, abaixo do código que você já tem, cole o seguinte código.

    ```
    fmt.Printf("Generic Sums with Constraint: %v and %v\n",
    	SumNumbers(ints),
    	SumNumbers(floats))
    ```

    Neste código, você:

    *   Chama `SumNumbers` com cada map, imprimindo a soma dos valores de
        cada um.

        Como na seção anterior, você omite os argumentos de tipo (os nomes de tipo
        entre colchetes) nas chamadas da função genérica. O compilador do Go
        consegue inferir o argumento de tipo a partir dos outros argumentos.

#### Execute o código

Na linha de comando, no diretório que contém o main.go, execute o código.

```
$ go run .
Non-Generic Sums: 46 and 62.97
Generic Sums: 46 and 62.97
Generic Sums, type parameters inferred: 46 and 62.97
Generic Sums with Constraint: 46 and 62.97
```

## Conclusão {#conclusion}

Muito bem! Você acabou de conhecer generics em Go.

Próximos tópicos sugeridos:

*   O [Tour do Go](/tour/) é uma ótima introdução passo a passo
    aos fundamentos do Go.
*   Você vai encontrar boas práticas úteis de Go descritas em
    [Effective Go](/doc/effective_go) e
    [Como escrever código Go](/doc/code).

## Código completo {#completed_code}

Você pode executar este programa no
[Go playground](/play/p/apNmfVwogK0). No playground,
basta clicar no botão **Run**.

```
package main

import "fmt"

type Number interface {
	int64 | float64
}

func main() {
	// Initialize a map for the integer values
	ints := map[string]int64{
		"first": 34,
		"second": 12,
	}

	// Initialize a map for the float values
	floats := map[string]float64{
		"first": 35.98,
		"second": 26.99,
	}

	fmt.Printf("Non-Generic Sums: %v and %v\n",
		SumInts(ints),
		SumFloats(floats))

	fmt.Printf("Generic Sums: %v and %v\n",
		SumIntsOrFloats[string, int64](ints),
		SumIntsOrFloats[string, float64](floats))

	fmt.Printf("Generic Sums, type parameters inferred: %v and %v\n",
		SumIntsOrFloats(ints),
		SumIntsOrFloats(floats))

	fmt.Printf("Generic Sums with Constraint: %v and %v\n",
		SumNumbers(ints),
		SumNumbers(floats))
}

// SumInts adds together the values of m.
func SumInts(m map[string]int64) int64 {
	var s int64
	for _, v := range m {
		s += v
	}
	return s
}

// SumFloats adds together the values of m.
func SumFloats(m map[string]float64) float64 {
	var s float64
	for _, v := range m {
		s += v
	}
	return s
}

// SumIntsOrFloats sums the values of map m. It supports both floats and integers
// as map values.
func SumIntsOrFloats[K comparable, V int64 | float64](m map[K]V) V {
	var s V
	for _, v := range m {
		s += v
	}
	return s
}

// SumNumbers sums the values of map m. It supports both integers
// and floats as map values.
func SumNumbers[K comparable, V Number](m map[K]V) V {
	var s V
	for _, v := range m {
		s += v
	}
	return s
}

<!--{
  "ia-translated": true,
  "Template": true,
  "Title": "Tutorial: Primeiros passos com fuzzing",
  "HideTOC": true,
  "Breadcrumb": true
}-->

Este tutorial apresenta o básico de fuzzing em Go. Com fuzzing, dados aleatórios
são executados contra o seu teste na tentativa de encontrar vulnerabilidades ou
entradas que causam falhas. Alguns exemplos de vulnerabilidades que podem ser
encontradas com fuzzing são injeção de SQL, buffer overflow, negação de serviço
e ataques de cross-site scripting.

Neste tutorial, você vai escrever um teste de fuzz para uma função simples,
executar o comando go, e depurar e corrigir problemas no código.

Para ajuda com a terminologia ao longo deste tutorial, veja o [glossário de
Go Fuzzing](/security/fuzz/#glossary).

Você vai percorrer as seguintes seções:

1. [Crie uma pasta para o seu código.](#create_folder)
2. [Adicione o código a ser testado.](#code_to_test)
3. [Adicione um teste unitário.](#unit_test)
4. [Adicione um teste de fuzz.](#fuzz_test)
5. [Corrija dois bugs.](#fix_invalid_string_error)
6. [Explore recursos adicionais.](#conclusion)

**Observação:** para outros tutoriais, veja [Tutoriais](/doc/tutorial/index.html).

**Observação:** o fuzzing em Go atualmente suporta um subconjunto dos tipos
embutidos, listados na [documentação de Go Fuzzing](/security/fuzz/#requirements), com suporte
a mais tipos embutidos a ser adicionado no futuro.

## Pré-requisitos

- **Go.** Recomendamos usar a versão mais recente do Go para acompanhar este tutorial.
  Para instruções de instalação, veja [Instalando o Go](/doc/install).
- **Uma ferramenta para editar o seu código.** Qualquer editor de texto que você tenha
  vai funcionar bem.
- **Um terminal de comandos.** O Go funciona bem com qualquer terminal no Linux e no Mac,
  e com PowerShell ou cmd no Windows.
- **Um ambiente que suporte fuzzing.** O fuzzing em Go com instrumentação de
  cobertura atualmente só está disponível nas arquiteturas AMD64 e ARM64.

## Crie uma pasta para o seu código {#create_folder}

Para começar, crie uma pasta para o código que você vai escrever.

1. Abra um prompt de comando e vá para o seu diretório home.

   No Linux ou no Mac:

   ```
   $ cd
   ```

   No Windows:

   ```
   C:\> cd %HOMEPATH%
   ```

   O restante do tutorial vai mostrar um $ como prompt. Os comandos que você usar
   vão funcionar no Windows também.

2. No prompt de comando, crie um diretório para o seu código chamado fuzz.

   ```
   $ mkdir fuzz
   $ cd fuzz
   ```

3. Crie um módulo para guardar o seu código.

   Execute o comando `go mod init`, passando o caminho do módulo do seu novo código.

   ```
   $ go mod init example/fuzz
   go: creating new go.mod: module example/fuzz
   ```

   **Observação:** para código de produção, você especificaria um caminho de módulo
   mais específico para as suas necessidades. Para mais detalhes, não deixe de ver
   [Gerenciando dependências](/doc/modules/managing-dependencies).

Em seguida, você vai adicionar um código simples para inverter uma string, que vamos
testar com fuzzing depois.

## Adicione o código a ser testado {#code_to_test}

Nesta etapa, você vai adicionar uma função para inverter uma string.

### Escreva o código

1.  Usando o seu editor de texto, crie um arquivo chamado main.go no diretório fuzz.
2.  No main.go, no topo do arquivo, cole a seguinte declaração de pacote.

    ```
    package main
    ```

    Um programa independente (em oposição a uma biblioteca) sempre fica no pacote `main`.

3.  Abaixo da declaração de pacote, cole a seguinte declaração de função.

    ```
    func Reverse(s string) string {
        b := []byte(s)
        for i, j := 0, len(b)-1; i {{raw "<"}} len(b)/2; i, j = i+1, j-1 {
            b[i], b[j] = b[j], b[i]
        }
        return string(b)
    }
    ```

    Esta função vai aceitar uma `string`, percorrê-la um `byte` por vez e
    retornar a string invertida no final.

    _Observação:_ este código é baseado na função `stringutil.Reverse` dentro de
    golang.org/x/example.

4.  No topo do main.go, abaixo da declaração de pacote, cole a seguinte função
    `main` para inicializar uma string, invertê-la, imprimir a saída e repetir.

    ```
    func main() {
        input := "The quick brown fox jumped over the lazy dog"
        rev := Reverse(input)
        doubleRev := Reverse(rev)
        fmt.Printf("original: %q\n", input)
        fmt.Printf("reversed: %q\n", rev)
        fmt.Printf("reversed again: %q\n", doubleRev)
    }
    ```

    Esta função vai executar algumas operações `Reverse`, depois imprimir a saída na
    linha de comando. Isso pode ser útil para ver o código em ação e, possivelmente,
    para depuração.

5.  A função `main` usa o pacote fmt, então você precisa importá-lo.

    As primeiras linhas do código devem ficar assim:

    ```
    package main

    import "fmt"
    ```

### Execute o código

Na linha de comando, no diretório que contém o main.go, execute o código.

```
$ go run .
original: "The quick brown fox jumped over the lazy dog"
reversed: "god yzal eht revo depmuj xof nworb kciuq ehT"
reversed again: "The quick brown fox jumped over the lazy dog"
```

Você pode ver a string original, o resultado de invertê-la, depois o resultado de
invertê-la novamente, que é equivalente à original.

Agora que o código está rodando, é hora de testá-lo.

## Adicione um teste unitário {#unit_test}

Nesta etapa, você vai escrever um teste unitário básico para a função `Reverse`.

### Escreva o código

1. Usando o seu editor de texto, crie um arquivo chamado reverse_test.go no diretório
   fuzz.
2. Cole o seguinte código no reverse_test.go.

   ```
   package main

   import (
       "testing"
   )

   func TestReverse(t *testing.T) {
       testcases := []struct {
           in, want string
       }{
           {"Hello, world", "dlrow ,olleH"},
           {" ", " "},
           {"!12345", "54321!"},
       }
       for _, tc := range testcases {
           rev := Reverse(tc.in)
           if rev != tc.want {
                   t.Errorf("Reverse: %q, want %q", rev, tc.want)
           }
       }
   }
   ```

   Este teste simples vai verificar se as strings de entrada listadas são
   invertidas corretamente.

### Execute o código

Execute o teste unitário usando `go test`

```
$ go test
PASS
ok      example/fuzz  0.013s
```

Em seguida, você vai transformar o teste unitário em um teste de fuzz.

## Adicione um teste de fuzz {#fuzz_test}

O teste unitário tem limitações, principalmente que cada entrada precisa ser
adicionada ao teste pelo desenvolvedor. Um benefício do fuzzing é que ele gera
entradas para o seu código e pode identificar casos extremos que os casos de
teste que você criou não alcançaram.

Nesta seção, você vai converter o teste unitário em um teste de fuzz para que
possa gerar mais entradas com menos trabalho!

Observe que você pode manter testes unitários, benchmarks e testes de fuzz no
mesmo arquivo *_test.go, mas, para este exemplo, você vai converter o teste
unitário em um teste de fuzz.

### Escreva o código

No seu editor de texto, substitua o teste unitário no reverse_test.go pelo seguinte
teste de fuzz.

```
func FuzzReverse(f *testing.F) {
    testcases := []string{"Hello, world", " ", "!12345"}
    for _, tc := range testcases {
        f.Add(tc)  // Use f.Add to provide a seed corpus
    }
    f.Fuzz(func(t *testing.T, orig string) {
        rev := Reverse(orig)
        doubleRev := Reverse(rev)
        if orig != doubleRev {
            t.Errorf("Before: %q, after: %q", orig, doubleRev)
        }
        if utf8.ValidString(orig) && !utf8.ValidString(rev) {
            t.Errorf("Reverse produced invalid UTF-8 string %q", rev)
        }
    })
}
```

O fuzzing também tem algumas limitações. No seu teste unitário, você poderia prever a
saída esperada da função `Reverse` e verificar se a saída real atendia a essas
expectativas.

Por exemplo, no caso de teste `Reverse("Hello, world")`, o teste unitário especifica
o retorno como `"dlrow ,olleH"`.

Ao fazer fuzzing, você não consegue prever a saída esperada, já que não tem
controle sobre as entradas.

No entanto, há algumas propriedades da função `Reverse` que você pode
verificar em um teste de fuzz. As duas propriedades verificadas neste teste de fuzz são:

1.  Inverter uma string duas vezes preserva o valor original
2.  A string invertida preserva seu estado como UTF-8 válido.

Observe as diferenças de sintaxe entre o teste unitário e o teste de fuzz:

- A função começa com FuzzXxx em vez de TestXxx, e recebe `*testing.F`
  em vez de `*testing.T`
- Onde você esperaria ver uma execução `t.Run`, você vê `f.Fuzz`,
  que recebe uma função alvo de fuzz cujos parâmetros são `*testing.T` e os
  tipos a serem testados com fuzzing. As entradas do seu teste unitário são fornecidas como
  entradas de corpus inicial usando `f.Add`.

Garanta que o novo pacote, `unicode/utf8`, foi importado.

```
package main

import (
    "testing"
    "unicode/utf8"
)
```

Com o teste unitário convertido em teste de fuzz, é hora de executar o teste novamente.

### Execute o código

1. Execute o teste de fuzz sem fazer fuzzing para garantir que as entradas iniciais passem.

   ```
   $ go test
   PASS
   ok      example/fuzz  0.013s
   ```

   Você também pode executar `go test -run=FuzzReverse` se tiver outros testes nesse
   arquivo e quiser rodar apenas o teste de fuzz.

2. Execute `FuzzReverse` com fuzzing, para ver se alguma entrada de string gerada
   aleatoriamente vai causar uma falha. Isso é executado usando `go test` com uma nova
   flag, `-fuzz`, definida com o parâmetro `Fuzz`. Copie o comando abaixo.

    ```
    $ go test -fuzz=Fuzz
    ```

    Outra flag útil é `-fuzztime`, que limita o tempo que o fuzzing leva.
    Por exemplo, especificar `-fuzztime 10s` no teste abaixo significaria que,
    desde que nenhuma falha ocorra antes, o teste sairia por padrão
    depois de 10 segundos. Veja [esta
    seção](https://pkg.go.dev/cmd/go#hdr-Testing_flags) da documentação do cmd/go
    para outras flags de teste.

   Agora, execute o comando que você acabou de copiar.

   ```
   $ go test -fuzz=Fuzz
   fuzz: elapsed: 0s, gathering baseline coverage: 0/3 completed
   fuzz: elapsed: 0s, gathering baseline coverage: 3/3 completed, now fuzzing with 8 workers
   fuzz: minimizing 38-byte failing input file...
   --- FAIL: FuzzReverse (0.01s)
       --- FAIL: FuzzReverse (0.00s)
           reverse_test.go:20: Reverse produced invalid UTF-8 string "\x9c\xdd"

       Failing input written to testdata/fuzz/FuzzReverse/af69258a12129d6cbba438df5d5f25ba0ec050461c116f777e77ea7c9a0d217a
       To re-run:
       go test -run=FuzzReverse/af69258a12129d6cbba438df5d5f25ba0ec050461c116f777e77ea7c9a0d217a
   FAIL
   exit status 1
   FAIL    example/fuzz  0.030s
   ```

   Uma falha ocorreu durante o fuzzing, e a entrada que causou o problema é
   gravada em um arquivo de corpus inicial que será executado na próxima vez que `go test` for
   chamado, mesmo sem a flag `-fuzz`. Para ver a entrada que causou a
   falha, abra o arquivo de corpus gravado no diretório testdata/fuzz/FuzzReverse
   em um editor de texto. Seu arquivo de corpus inicial pode conter uma string
   diferente, mas o formato será o mesmo.

   ```
   go test fuzz v1
   string("泃")
   ```

   A primeira linha do arquivo de corpus indica a versão de codificação. Cada
   linha seguinte representa o valor de cada tipo que compõe a entrada do corpus.
   Como o alvo de fuzz recebe apenas 1 entrada, há apenas 1 valor depois da
   versão.

3. Execute `go test` novamente sem a flag `-fuzz`; a nova entrada de corpus inicial
   que falhou será usada:

   ```
   $ go test
   --- FAIL: FuzzReverse (0.00s)
       --- FAIL: FuzzReverse/af69258a12129d6cbba438df5d5f25ba0ec050461c116f777e77ea7c9a0d217a (0.00s)
           reverse_test.go:20: Reverse produced invalid string
   FAIL
   exit status 1
   FAIL    example/fuzz  0.016s
   ```

   Como nosso teste falhou, é hora de depurar.

## Corrija o erro de string inválida {#fix_invalid_string_error}

Nesta seção, você vai depurar a falha e corrigir o bug.

Fique à vontade para passar um tempo pensando nisso e tentando corrigir o problema
por conta própria antes de seguir em frente.

### Diagnostique o erro

Há algumas maneiras diferentes de depurar este erro. Se você estiver usando o VS
Code como editor de texto, pode [configurar o seu
depurador](https://github.com/golang/vscode-go/blob/master/docs/debugging.md) para
investigar.

Neste tutorial, vamos registrar informações úteis de depuração no seu terminal.

Primeiro, considere a documentação de
[`utf8.ValidString`](https://pkg.go.dev/unicode/utf8).

```
ValidString reports whether s consists entirely of valid UTF-8-encoded runes.
```

A função `Reverse` atual inverte a string byte a byte, e aí está o nosso problema. Para
preservar as runes codificadas em UTF-8 da string original, devemos, em vez disso,
inverter a string rune a rune.

Para examinar por que a entrada (neste caso, o caractere chinês `泃`) faz
`Reverse` produzir uma string inválida ao ser invertida, você pode inspecionar o número
de runes na string invertida.

#### Escreva o código

No seu editor de texto, substitua o alvo de fuzz dentro de `FuzzReverse` pelo
seguinte.

```
f.Fuzz(func(t *testing.T, orig string) {
    rev := Reverse(orig)
    doubleRev := Reverse(rev)
    t.Logf("Number of runes: orig=%d, rev=%d, doubleRev=%d", utf8.RuneCountInString(orig), utf8.RuneCountInString(rev), utf8.RuneCountInString(doubleRev))
    if orig != doubleRev {
        t.Errorf("Before: %q, after: %q", orig, doubleRev)
    }
    if utf8.ValidString(orig) && !utf8.ValidString(rev) {
        t.Errorf("Reverse produced invalid UTF-8 string %q", rev)
    }
})
```

Esta linha `t.Logf` vai imprimir na linha de comando se um erro ocorrer, ou se
executar o teste com `-v`, o que pode ajudar você a depurar este problema específico.

#### Execute o código

Execute o teste usando go test

```
$ go test
--- FAIL: FuzzReverse (0.00s)
    --- FAIL: FuzzReverse/28f36ef487f23e6c7a81ebdaa9feffe2f2b02b4cddaa6252e87f69863046a5e0 (0.00s)
        reverse_test.go:16: Number of runes: orig=1, rev=3, doubleRev=1
        reverse_test.go:21: Reverse produced invalid UTF-8 string "\x83\xb3\xe6"
FAIL
exit status 1
FAIL    example/fuzz    0.598s
```

O corpus inicial inteiro usava strings em que cada caractere era um único byte.
No entanto, caracteres como 泃 podem exigir vários bytes. Assim, inverter a
string byte a byte invalida os caracteres de múltiplos bytes.

**Observação:** se você tiver curiosidade sobre como o Go lida com strings, leia o post do blog
[Strings, bytes, runes and characters in Go](/blog/strings) para
um entendimento mais profundo.

Com um entendimento melhor do bug, corrija o erro na função `Reverse`.

### Corrija o erro

Para corrigir a função `Reverse`, vamos percorrer a string por runes, em vez de
por bytes.

#### Escreva o código

No seu editor de texto, substitua a função Reverse() existente pela seguinte.

```
func Reverse(s string) string {
    r := []rune(s)
    for i, j := 0, len(r)-1; i {{raw "<"}} len(r)/2; i, j = i+1, j-1 {
        r[i], r[j] = r[j], r[i]
    }
    return string(r)
}
```

A diferença principal é que `Reverse` agora itera sobre cada `rune` da
string, em vez de cada `byte`. Observe que este é apenas um exemplo e não
trata [caracteres combinados](https://en.wikipedia.org/wiki/Combining_character) corretamente.

#### Execute o código

1. Execute o teste usando `go test`

   ```
   $ go test
   PASS
   ok      example/fuzz  0.016s
   ```

   O teste agora passa!

2. Faça fuzzing novamente com `go test -fuzz`, para ver se há novos bugs.

   ```
   $ go test -fuzz=Fuzz
   fuzz: elapsed: 0s, gathering baseline coverage: 0/37 completed
   fuzz: minimizing 506-byte failing input file...
   fuzz: elapsed: 0s, gathering baseline coverage: 5/37 completed
   --- FAIL: FuzzReverse (0.02s)
       --- FAIL: FuzzReverse (0.00s)
           reverse_test.go:33: Before: "\x91", after: "�"

       Failing input written to testdata/fuzz/FuzzReverse/1ffc28f7538e29d79fce69fef20ce5ea72648529a9ca10bea392bcff28cd015c
       To re-run:
       go test -run=FuzzReverse/1ffc28f7538e29d79fce69fef20ce5ea72648529a9ca10bea392bcff28cd015c
   FAIL
   exit status 1
   FAIL    example/fuzz  0.032s
   ```

   Podemos ver que a string é diferente da original depois de ser
   invertida duas vezes. Desta vez, a própria entrada é um unicode inválido. Como isso é
   possível se estamos fazendo fuzzing com strings?

   Vamos depurar de novo.

## Corrija o erro de dupla inversão {#fix_double_reverse_error}

Nesta seção, você vai depurar a falha de dupla inversão e corrigir o bug.

Fique à vontade para passar um tempo pensando nisso e tentando corrigir o problema
por conta própria antes de seguir em frente.

### Diagnostique o erro

Como antes, há várias maneiras de depurar esta falha. Neste caso,
usar um
[depurador](https://github.com/golang/vscode-go/blob/master/docs/debugging.md)
seria uma ótima abordagem.

Neste tutorial, vamos registrar informações úteis de depuração na função `Reverse`.

Observe com atenção a string invertida para encontrar o erro. Em Go, [uma string é um
slice somente leitura de bytes](/blog/strings), e pode conter bytes
que não são UTF-8 válido. A string original é um slice de bytes com um byte,
`'\x91'`. Quando a string de entrada é convertida para `[]rune`, o Go codifica o slice de bytes
em UTF-8 e substitui o byte pelo caractere UTF-8 �. Quando comparamos o
caractere UTF-8 de substituição com o slice de bytes de entrada, eles claramente não são iguais.

#### Escreva o código

1. No seu editor de texto, substitua a função `Reverse` pela seguinte.

   ```
   func Reverse(s string) string {
       fmt.Printf("input: %q\n", s)
       r := []rune(s)
       fmt.Printf("runes: %q\n", r)
       for i, j := 0, len(r)-1; i {{raw "<"}} len(r)/2; i, j = i+1, j-1 {
           r[i], r[j] = r[j], r[i]
       }
       return string(r)
   }
   ```

   Isso vai ajudar a entender o que está dando errado ao converter a string
   para um slice de runes.

#### Execute o código

Desta vez, queremos apenas executar o teste que falha para inspecionar os logs. Para
fazer isso, vamos usar `go test -run`.

Para executar uma entrada específica do corpus dentro de FuzzXxx/testdata, você pode passar
{FuzzTestName}/{filename} para `-run`. Isso pode ser útil na depuração.
Neste caso, defina a flag `-run` igual ao hash exato do teste que falha.
Copie e cole o hash único do seu terminal;
ele será diferente do que está abaixo.

```
$ go test -run=FuzzReverse/28f36ef487f23e6c7a81ebdaa9feffe2f2b02b4cddaa6252e87f69863046a5e0
input: "\x91"
runes: ['�']
input: "�"
runes: ['�']
--- FAIL: FuzzReverse (0.00s)
    --- FAIL: FuzzReverse/28f36ef487f23e6c7a81ebdaa9feffe2f2b02b4cddaa6252e87f69863046a5e0 (0.00s)
        reverse_test.go:16: Number of runes: orig=1, rev=1, doubleRev=1
        reverse_test.go:18: Before: "\x91", after: "�"
FAIL
exit status 1
FAIL    example/fuzz    0.145s
```

Sabendo que a entrada é um unicode inválido, vamos corrigir o erro na nossa
função `Reverse`.

### Corrija o erro

Para corrigir este problema, vamos fazer a função `Reverse` retornar um erro se a entrada
não for UTF-8 válido.

#### Escreva o código

1. No seu editor de texto, substitua a função `Reverse` existente pela
   seguinte.

   ```
   func Reverse(s string) (string, error) {
       if !utf8.ValidString(s) {
           return s, errors.New("input is not valid UTF-8")
       }
       r := []rune(s)
       for i, j := 0, len(r)-1; i {{raw "<"}} len(r)/2; i, j = i+1, j-1 {
           r[i], r[j] = r[j], r[i]
       }
       return string(r), nil
   }
   ```

   Essa mudança vai retornar um erro se a string de entrada contiver caracteres
   que não são UTF-8 válido.

1. Como a função Reverse agora retorna um erro, modifique a função `main` para
   descartar o valor extra de erro. Substitua a função `main` existente pela
   seguinte.

   ```
   func main() {
       input := "The quick brown fox jumped over the lazy dog"
       rev, revErr := Reverse(input)
       doubleRev, doubleRevErr := Reverse(rev)
       fmt.Printf("original: %q\n", input)
       fmt.Printf("reversed: %q, err: %v\n", rev, revErr)
       fmt.Printf("reversed again: %q, err: %v\n", doubleRev, doubleRevErr)
   }
   ```

    Essas chamadas a `Reverse` devem retornar um erro nil, já que a string de
    entrada é UTF-8 válido.

1. Você vai precisar importar os pacotes errors e unicode/utf8.
   A instrução import no main.go deve ficar assim:

   ```
   import (
       "errors"
       "fmt"
       "unicode/utf8"
   )
   ```

1. Modifique o arquivo reverse_test.go para verificar erros e pular o teste se
   forem gerados erros, retornando.

   ```
   func FuzzReverse(f *testing.F) {
       testcases := []string {"Hello, world", " ", "!12345"}
       for _, tc := range testcases {
           f.Add(tc)  // Use f.Add to provide a seed corpus
       }
       f.Fuzz(func(t *testing.T, orig string) {
           rev, err1 := Reverse(orig)
           if err1 != nil {
               return
           }
           doubleRev, err2 := Reverse(rev)
           if err2 != nil {
                return
           }
           if orig != doubleRev {
               t.Errorf("Before: %q, after: %q", orig, doubleRev)
           }
           if utf8.ValidString(orig) && !utf8.ValidString(rev) {
               t.Errorf("Reverse produced invalid UTF-8 string %q", rev)
           }
       })
   }
   ```

   Em vez de retornar, você também pode chamar `t.Skip()` para interromper a execução
   daquela entrada de fuzz.

#### Execute o código

1. Execute o teste usando go test

   ```
   $ go test
   PASS
   ok      example/fuzz  0.019s
   ```

2.  Faça fuzzing com `go test -fuzz=Fuzz`, depois que alguns segundos tiverem passado, pare
    o fuzzing com `ctrl-C`. O teste de fuzz vai rodar até encontrar uma
    entrada que falha, a menos que você passe a flag `-fuzztime`. O padrão é rodar para sempre se nenhuma
    falha ocorrer, e o processo pode ser interrompido com `ctrl-C`.

   ```
   $ go test -fuzz=Fuzz
   fuzz: elapsed: 0s, gathering baseline coverage: 0/38 completed
   fuzz: elapsed: 0s, gathering baseline coverage: 38/38 completed, now fuzzing with 4 workers
   fuzz: elapsed: 3s, execs: 86342 (28778/sec), new interesting: 2 (total: 35)
   fuzz: elapsed: 6s, execs: 193490 (35714/sec), new interesting: 4 (total: 37)
   fuzz: elapsed: 9s, execs: 304390 (36961/sec), new interesting: 4 (total: 37)
   ...
   fuzz: elapsed: 3m45s, execs: 7246222 (32357/sec), new interesting: 8 (total: 41)
   ^Cfuzz: elapsed: 3m48s, execs: 7335316 (31648/sec), new interesting: 8 (total: 41)
   PASS
   ok      example/fuzz  228.000s
   ```

3. Faça fuzzing com `go test -fuzz=Fuzz -fuzztime 30s`, que vai fazer fuzzing por 30
   segundos antes de sair, se nenhuma falha for encontrada.

   ```
   $ go test -fuzz=Fuzz -fuzztime 30s
   fuzz: elapsed: 0s, gathering baseline coverage: 0/5 completed
   fuzz: elapsed: 0s, gathering baseline coverage: 5/5 completed, now fuzzing with 4 workers
   fuzz: elapsed: 3s, execs: 80290 (26763/sec), new interesting: 12 (total: 12)
   fuzz: elapsed: 6s, execs: 210803 (43501/sec), new interesting: 14 (total: 14)
   fuzz: elapsed: 9s, execs: 292882 (27360/sec), new interesting: 14 (total: 14)
   fuzz: elapsed: 12s, execs: 371872 (26329/sec), new interesting: 14 (total: 14)
   fuzz: elapsed: 15s, execs: 517169 (48433/sec), new interesting: 15 (total: 15)
   fuzz: elapsed: 18s, execs: 663276 (48699/sec), new interesting: 15 (total: 15)
   fuzz: elapsed: 21s, execs: 771698 (36143/sec), new interesting: 15 (total: 15)
   fuzz: elapsed: 24s, execs: 924768 (50990/sec), new interesting: 16 (total: 16)
   fuzz: elapsed: 27s, execs: 1082025 (52427/sec), new interesting: 17 (total: 17)
   fuzz: elapsed: 30s, execs: 1172817 (30281/sec), new interesting: 17 (total: 17)
   fuzz: elapsed: 31s, execs: 1172817 (0/sec), new interesting: 17 (total: 17)
   PASS
   ok      example/fuzz  31.025s
   ```

   O fuzzing passou!

   Além da flag `-fuzz`, várias novas flags foram adicionadas ao `go
   test` e podem ser vistas na [documentação](/security/fuzz/#custom-settings).

   Veja [Go Fuzzing](/security/fuzz/#command-line-output) para mais
   informações sobre os termos usados na saída do fuzzing. Por exemplo, "new interesting"
   se refere a entradas que expandem a cobertura de código do corpus existente do
   teste de fuzz. Pode-se esperar que o número de entradas "new interesting" aumente
   bruscamente quando o fuzzing começa, tenha picos várias vezes à medida que novos caminhos de código são
   descobertos, e depois diminua com o tempo.

## Conclusão {#conclusion}

Muito bem! Você acabou de se apresentar ao fuzzing em Go.

O próximo passo é escolher uma função no seu código que você gostaria de testar com fuzzing e
experimentar! Se o fuzzing encontrar um bug no seu código, considere adicioná-lo à
[galeria de troféus](/wiki/Fuzzing-trophy-case).

Se você tiver algum problema ou uma ideia para um recurso, [abra uma
issue](/issue/new/?&labels=fuzz).

Para discussões e feedback geral sobre o recurso, você também pode participar do
[canal #fuzzing](https://gophers.slack.com/archives/CH5KV1AKE) no
Gophers Slack.

Confira a documentação em [go.dev/security/fuzz](/security/fuzz/#requirements) para
leituras adicionais.

## Código completo

--- main.go ---

```
package main

import (
    "errors"
    "fmt"
    "unicode/utf8"
)

func main() {
    input := "The quick brown fox jumped over the lazy dog"
    rev, revErr := Reverse(input)
    doubleRev, doubleRevErr := Reverse(rev)
    fmt.Printf("original: %q\n", input)
    fmt.Printf("reversed: %q, err: %v\n", rev, revErr)
    fmt.Printf("reversed again: %q, err: %v\n", doubleRev, doubleRevErr)
}

func Reverse(s string) (string, error) {
    if !utf8.ValidString(s) {
        return s, errors.New("input is not valid UTF-8")
    }
    r := []rune(s)
    for i, j := 0, len(r)-1; i {{raw "<"}} len(r)/2; i, j = i+1, j-1 {
        r[i], r[j] = r[j], r[i]
    }
    return string(r), nil
}
```

--- reverse_test.go ---

```
package main

import (
    "testing"
    "unicode/utf8"
)

func FuzzReverse(f *testing.F) {
    testcases := []string{"Hello, world", " ", "!12345"}
    for _, tc := range testcases {
        f.Add(tc) // Use f.Add to provide a seed corpus
    }
    f.Fuzz(func(t *testing.T, orig string) {
        rev, err1 := Reverse(orig)
        if err1 != nil {
            return
        }
        doubleRev, err2 := Reverse(rev)
        if err2 != nil {
            return
        }
        if orig != doubleRev {
            t.Errorf("Before: %q, after: %q", orig, doubleRev)
        }
        if utf8.ValidString(orig) && !utf8.ValidString(rev) {
            t.Errorf("Reverse produced invalid UTF-8 string %q", rev)
        }
    })
}
```

[Voltar ao topo](#top)

<!--{
  "ia-translated": true,
  "Title": "Tutorial: Encontrar e corrigir dependências vulneráveis com govulncheck",
  "HideTOC": true,
  "Breadcrumb": true
}-->

Govulncheck é uma ferramenta de baixo ruído que ajuda você a encontrar e corrigir
dependências vulneráveis nos seus projetos Go. Ela faz isso analisando as
dependências do projeto em busca de vulnerabilidades conhecidas e, em seguida,
identificando qualquer chamada direta ou indireta a essas vulnerabilidades no
seu código.

Neste tutorial, você vai aprender a usar o govulncheck para analisar um programa
simples em busca de vulnerabilidades. Você também vai aprender a priorizar e
avaliar vulnerabilidades, para concentrar seus esforços primeiro nas mais
importantes.

Para saber mais sobre o govulncheck, veja a
[documentação do govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck)
e este [post do blog sobre gestão de vulnerabilidades](/blog/vuln) em Go.
Também adoraríamos [ouvir o seu feedback](/s/govulncheck-feedback).

## Pré-requisitos

- **Go.** Recomendamos usar a versão mais recente do Go para seguir este tutorial.
  Para as instruções de instalação, veja [Instalando o Go](/doc/install).
- **Um editor de código.** Qualquer editor que você tenha vai funcionar bem.
- **Um terminal de linha de comando.** O Go funciona bem em qualquer terminal no Linux e no Mac, e no PowerShell ou no cmd do Windows.

O tutorial vai guiar você pelos seguintes passos:

1. Criar um módulo Go de exemplo com uma dependência vulnerável
2. Instalar e executar o govulncheck
3. Avaliar as vulnerabilidades
4. Atualizar as dependências vulneráveis

## Criar um módulo Go de exemplo com uma dependência vulnerável

**Passo 1.** Para começar, crie uma nova pasta chamada `vuln-tutorial` e inicialize um módulo Go.
(Se você é novo nos módulos Go, veja [go.dev/doc/tutorial/create-module](/doc/tutorial/create-module).

Por exemplo, a partir do seu diretório home, execute o seguinte:

```
$ mkdir vuln-tutorial
$ cd vuln-tutorial
$ go mod init vuln.tutorial
```

**Passo 2.** Crie um arquivo chamado `main.go` dentro da pasta `vuln-tutorial` e copie
o código a seguir para dentro dele:

```
package main

import (
        "fmt"
        "os"

        "golang.org/x/text/language"
)

func main() {
        for _, arg := range os.Args[1:] {
                tag, err := language.Parse(arg)
                if err != nil {
                        fmt.Printf("%s: error: %v\n", arg, err)
                } else if tag == language.Und {
                        fmt.Printf("%s: undefined\n", arg)
                } else {
                        fmt.Printf("%s: tag %s\n", arg, tag)
                }
        }
}
```

Este programa de exemplo recebe uma lista de tags de idioma como argumentos da
linha de comando e imprime uma mensagem para cada tag, indicando se ela foi
interpretada com sucesso, se a tag é indefinida ou se houve erro ao interpretá-la.

**Passo 3.** Execute `go mod tidy`, que vai preencher o arquivo `go.mod` com todas as
dependências exigidas pelo código que você adicionou em `main.go` no passo anterior.

Na pasta `vuln-tutorial`, execute:

```
$ go mod tidy
```

Você deve ver esta saída:

```
go: finding module for package golang.org/x/text/language
go: downloading golang.org/x/text v0.9.0
go: found golang.org/x/text/language in golang.org/x/text v0.9.0
```

**Passo 4.** Abra o seu arquivo `go.mod` para verificar se ele está assim:

```
module vuln.tutorial

go 1.20

require golang.org/x/text v0.9.0
```

**Passo 5.** Faça o downgrade da versão de `golang.org/x/text` para a v0.3.5, que contém
vulnerabilidades conhecidas. Execute:

```
$ go get golang.org/x/text@v0.3.5
```

Você deve ver esta saída:

```
go: downgraded golang.org/x/text v0.9.0 => v0.3.5
```

O arquivo `go.mod` agora deve estar assim:

```
module vuln.tutorial

go 1.20

require golang.org/x/text v0.3.5
```

Agora, vamos ver o govulncheck em ação.


## Instalar e executar o govulncheck

**Passo 6.** Instale o govulncheck com o comando `go install`:

```
$ go install golang.org/x/vuln/cmd/govulncheck@latest
```

**Passo 7.** Na pasta que você quer analisar (neste caso, `vuln-tutorial`), execute:

```
$ govulncheck ./...
```

Você deve ver esta saída:

```
govulncheck is an experimental tool. Share feedback at https://go.dev/s/govulncheck-feedback.

Using go1.20.3 and govulncheck@v0.0.0 with
vulnerability data from https://vuln.go.dev (last modified 2023-04-18 21:32:26 +0000 UTC).

Scanning your code and 46 packages across 1 dependent module for known vulnerabilities...
Your code is affected by 1 vulnerability from 1 module.

Vulnerability #1: GO-2021-0113
  Due to improper index calculation, an incorrectly formatted
  language tag can cause Parse to panic via an out of bounds read.
  If Parse is used to process untrusted user inputs, this may be
  used as a vector for a denial of service attack.

  More info: https://pkg.go.dev/vuln/GO-2021-0113

  Module: golang.org/x/text
    Found in: golang.org/x/text@v0.3.5
    Fixed in: golang.org/x/text@v0.3.7

    Call stacks in your code:
      main.go:12:29: vuln.tutorial.main calls golang.org/x/text/language.Parse

=== Informational ===

Found 1 vulnerability in packages that you import, but there are no call
stacks leading to the use of this vulnerability. You may not need to
take any action. See https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck
for details.

Vulnerability #1: GO-2022-1059
  An attacker may cause a denial of service by crafting an
  Accept-Language header which ParseAcceptLanguage will take
  significant time to parse.
  More info: https://pkg.go.dev/vuln/GO-2022-1059
  Found in: golang.org/x/text@v0.3.5
  Fixed in: golang.org/x/text@v0.3.8

```

### Interpretando a saída

<font size="2">  *Observação: se você não estiver usando a versão mais recente do Go,
pode ver vulnerabilidades adicionais da biblioteca padrão. </font>

Nosso código é afetado por uma vulnerabilidade,
[GO-2021-0113](https://pkg.go.dev/vuln/GO-2021-0113), porque ele chama diretamente
a função `Parse` de `golang.org/x/text/language` em uma versão vulnerável
(v0.3.5).

Outra vulnerabilidade, [GO-2022-1059](https://pkg.go.dev/vuln/GO-2022-1059),
existe no módulo `golang.org/x/text` na v0.3.5. No entanto, ela é reportada como
"Informational" porque o nosso código nunca chama (direta ou indiretamente) nenhuma
das funções vulneráveis dela.

Agora, vamos avaliar as vulnerabilidades e decidir qual ação tomar.

### Avaliar as vulnerabilidades

a. Avalie as vulnerabilidades.

Primeiro, leia a descrição da vulnerabilidade e determine se ela realmente se
aplica ao seu código e ao seu caso de uso. Se precisar de mais informações,
acesse o link "More info".

Pela descrição, a vulnerabilidade GO-2021-0113 pode causar um panic quando
`Parse` é usada para processar entradas de usuários não confiáveis. Vamos supor
que o nosso programa deva suportar entradas não confiáveis e que estamos
preocupados com negação de serviço, então a vulnerabilidade provavelmente se aplica.

A GO-2022-1059 provavelmente não afeta o nosso código, porque ele não chama
nenhuma das funções vulneráveis desse relatório.

b. Decida uma ação.

Para mitigar a GO-2021-0113, temos algumas opções:
- **Opção 1: Atualizar para uma versão corrigida.** Se houver uma correção disponível,
  podemos remover a dependência vulnerável atualizando para uma versão corrigida do módulo.
- **Opção 2: Parar de usar os símbolos vulneráveis.** Poderíamos optar por
  remover todas as chamadas à função vulnerável no nosso código.
  Teríamos de encontrar uma alternativa ou implementá-la nós mesmos.

Neste caso, há uma correção disponível, e a função `Parse` é parte essencial do
nosso programa. Vamos atualizar a nossa dependência para a versão indicada em
"Fixed in", a v0.3.7.

Decidimos adiar a correção da vulnerabilidade informativa GO-2022-1059, mas, como
ela está no mesmo módulo que a GO-2021-0113, e como a versão corrigida dela é a
v0.3.8, podemos remover as duas de uma só vez atualizando para a v0.3.8.

## Atualizar as dependências vulneráveis

Felizmente, atualizar dependências vulneráveis é bem simples.

**Passo 8.** Atualize `golang.org/x/text` para a v0.3.8:

```
$ go get golang.org/x/text@v0.3.8
```

Você deve ver esta saída:

```
go: upgraded golang.org/x/text v0.3.5 => v0.3.8
```

(Observe que poderíamos ter escolhido atualizar para `latest`, ou para qualquer
outra versão posterior à v0.3.8.)

**Passo 9.** Agora, execute o govulncheck novamente:

```
$ govulncheck ./...
```

Você verá esta saída:

```
govulncheck is an experimental tool. Share feedback at https://go.dev/s/govulncheck-feedback.

Using go1.20.3 and govulncheck@v0.0.0 with
vulnerability data from https://vuln.go.dev (last modified 2023-04-06 19:19:26 +0000 UTC).

Scanning your code and 46 packages across 1 dependent module for known vulnerabilities...
No vulnerabilities found.
```

Por fim, o govulncheck confirma que nenhuma vulnerabilidade foi encontrada.

Ao analisar regularmente as suas dependências com o comando govulncheck, você
protege a sua base de código identificando, priorizando e corrigindo
vulnerabilidades.

<!--{
  "ia-translated": true,
  "Title": "Tutorial: Trabalhando com JSON",
  "Breadcrumb": true
}-->

JSON (JavaScript Object Notation) é um formato simples de troca de dados.
Sintaticamente, ele se parece com os objetos e listas do JavaScript.
É muito usado para comunicação com serviços de API em rede,
mas também aparece em muitos outros lugares.
A página oficial, [json.org](http://json.org),
traz uma definição excelente, clara e concisa do padrão.

Com o [pacote encoding/json/v2](/pkg/encoding/json/v2), é muito simples ler
e escrever dados JSON nos seus programas em Go.
Esse pacote oferece uma API mais limpa e padrões melhores do que o pacote mais
antigo [encoding/json](/pkg/encoding/json).

## Codificação

Para codificar dados JSON, usamos a função [`Marshal`](/pkg/encoding/json/v2#Marshal).

```
func Marshal(in any, opts ...Options) (out []byte, err error)
```

Dada a estrutura de dados do Go, `Message`,

```
type Message struct {
	Name string
	Body string
	Time time.Time
}
```

e uma instância de `Message`

```
m := Message{"Alice", "Hello", time.Date(2011, 1, 25, 0, 0, 0, 0, time.UTC)}
```

podemos fazer o marshal de uma versão JSON de `m` usando `json.Marshal`:

```
b, err := json.Marshal(m)
```

Se tudo correr bem, `err` será `nil` e `b` será um `[]byte` contendo estes dados JSON:

```
b == []byte(`{"Name":"Alice","Body":"Hello","Time":"2011-01-25T00:00:00Z"}`)
```

Só são codificadas estruturas de dados que podem ser representadas como JSON válido:

  - Ponteiros são codificados como os valores para os quais apontam (ou como `null` se o ponteiro for `nil`).

  - Objetos JSON só aceitam strings como chaves.
    Assim, para codificar um map do Go, ele precisa ter uma chave que seja codificada como string JSON,
    como `map[string]T` (em que `T` é qualquer tipo do Go suportado pelo pacote
    json).

  - Tipos de canal, complexos e funções não podem ser codificados.

  - Estruturas de dados cíclicas não são suportadas.

  - [`Marshal`](/pkg/encoding/json/v2#Marshal) documenta o conjunto completo da semântica de codificação.

O pacote json só acessa os campos exportados de tipos struct (aqueles
que começam com letra maiúscula).
Por isso, apenas os campos exportados de uma struct aparecem na saída JSON.

## Decodificação

Para decodificar dados JSON, usamos a função [`Unmarshal`](/pkg/encoding/json/v2#Unmarshal).

```
func Unmarshal(in []byte, out any, opts ...Options) (err error)
```

Primeiro, precisamos criar um lugar onde os dados decodificados serão armazenados

```
var m Message
```

e chamar `json.Unmarshal`, passando a ela um `[]byte` com os dados JSON e um ponteiro para `m`

```
err := json.Unmarshal(b, &m)
```

Se `b` contiver JSON válido que caiba em `m`,
depois da chamada `err` será `nil` e os dados de `b` terão sido
armazenados na struct `m`,
como se fosse feita uma atribuição como:

```
m = Message{
	Name: "Alice",
	Body: "Hello",
	Time: time.Date(2011, 1, 25, 0, 0, 0, 0, time.UTC),
}
```

Como o `Unmarshal` identifica os campos onde deve guardar os dados decodificados?
Para uma chave JSON `"Foo"`,
o `Unmarshal` procura nos campos da struct de destino (em
ordem de preferência):

  - Um campo exportado com a tag `json:"Foo"` (veja a [especificação da linguagem Go](/ref/spec#Struct_types)
    para mais sobre tags de struct), ou

  - Um campo exportado chamado `Foo`.

E o que acontece quando a estrutura dos dados JSON não bate exatamente com o tipo do Go?

```
b := []byte(`{"Name":"Bob","Food":"Pickle"}`)
var m Message
err := json.Unmarshal(b, &m)
```

O `Unmarshal` decodifica apenas os campos que consegue encontrar no tipo de destino.
Nesse caso, só o campo `Name` de `m` será preenchido,
e o campo `Food` será ignorado.
Esse comportamento é especialmente útil quando você quer extrair apenas alguns
campos específicos de um JSON grande.
Isso também significa que quaisquer campos não exportados da struct de destino
não são afetados pelo `Unmarshal`.

Mas e se você não souber a estrutura dos seus dados JSON de antemão?

## JSON genérico com `any`

O tipo `any` descreve qualquer tipo do Go.
`any` é definido como `interface{}` (interface vazia), que descreve uma interface sem métodos.
Todo tipo do Go implementa pelo menos zero métodos e, portanto, satisfaz a interface vazia.

`any` funciona como um tipo contêiner genérico:

	var a any
	a = "a string"
	a = 2011
	a = 2.777

Uma asserção de tipo acessa o tipo concreto subjacente:

	r := a.(float64)
	fmt.Println("the circle's area", math.Pi*r*r)

Ou, se o tipo subjacente for desconhecido, um switch de tipo determina o tipo:

	switch v := a.(type) {
	case int:
	    fmt.Println("twice a is", v*2)
	case float64:
	    fmt.Println("the reciprocal of a is", 1/v)
	case string:
	    h := len(v) / 2
	    fmt.Println("a swapped by halves is", v[h:]+v[:h])
	default:
	    // a isn't one of the types above
	}

O pacote json usa valores `map[string]any` e
`[]any` para armazenar objetos e arrays JSON arbitrários;
ele aceita de bom grado fazer o unmarshal de qualquer JSON válido
em um valor `any` simples. Os tipos concretos padrão do Go são:

  - `bool` para booleanos JSON,

  - `float64` para números JSON,

  - `string` para strings JSON, e

  - `nil` para null JSON.

## Decodificando dados arbitrários

Considere estes dados JSON, armazenados na variável `b`:

```
b := []byte(`{"Name":"Wednesday","Age":6,"Parents":["Gomez","Morticia"]}`)
```

Sem saber a estrutura desses dados, podemos decodificá-los em um valor `any` com `Unmarshal`:

```
var f any
err := json.Unmarshal(b, &f)
```

Neste ponto, o valor do Go em `f` seria um map cujas chaves são strings
e cujos valores são, por sua vez, armazenados como valores `any`:

```
f = map[string]any{
	"Name": "Wednesday",
	"Age":  6,
	"Parents": []any{
		"Gomez",
		"Morticia",
	},
}
```

Para acessar esses dados, podemos usar uma asserção de tipo para obter o `map[string]any` subjacente de `f`:

```
m := f.(map[string]any)
```

Depois, podemos percorrer o map com uma instrução range e usar um switch de tipo
para acessar seus valores como os tipos concretos:

```
for k, v := range m {
	switch vv := v.(type) {
	case string:
		fmt.Println(k, "is string", vv)
	case float64:
		fmt.Println(k, "is float64", vv)
	case []any:
		fmt.Println(k, "is an array:")
		for i, u := range vv {
			fmt.Println(i, u)
		}
	default:
		fmt.Println(k, "is of a type I don't know how to handle")
	}
}
```

Dessa forma, você pode trabalhar com dados JSON desconhecidos e ainda aproveitar os benefícios da segurança de tipos.

## Tipos de referência

Vamos definir um tipo do Go para conter os dados do exemplo anterior:

```
type FamilyMember struct {
	Name    string
	Age     int
	Parents []string
}

var m FamilyMember
err := json.Unmarshal(b, &m)
```

Fazer o unmarshal desses dados em um valor `FamilyMember` funciona como esperado,
mas, se olharmos com atenção, podemos notar algo notável que aconteceu.
Com a instrução var, alocamos uma struct `FamilyMember` e
passamos um ponteiro para esse valor ao `Unmarshal`,
mas, naquele momento, o campo `Parents` era um valor de slice `nil`.
Para preencher o campo `Parents`, o `Unmarshal` alocou uma nova slice por trás dos panos.
Isso é típico da forma como o `Unmarshal` trabalha com os tipos de referência suportados
(ponteiros, slices e maps).

Considere fazer o unmarshal nesta estrutura de dados:

```
type Foo struct {
	Bar *Bar
}
```

Se houvesse um campo `Bar` no objeto JSON,
o `Unmarshal` alocaria um novo `Bar` e o preencheria.
Se não houvesse, `Bar` ficaria como um ponteiro `nil`.

Disso surge um padrão útil: se você tiver uma aplicação que recebe
alguns tipos distintos de mensagem,
você pode definir uma estrutura "receptora" como

```
type IncomingMessage struct {
	Cmd *Command
	Msg *Message
}
```

e a parte que envia pode preencher o campo `Cmd` e/ou o campo `Msg`
do objeto JSON de nível superior,
dependendo do tipo de mensagem que quer comunicar.
O `Unmarshal`, ao decodificar o JSON em uma struct `IncomingMessage`,
só alocará as estruturas de dados presentes nos dados JSON.
Para saber quais mensagens processar, o programador só precisa testar se
`Cmd` ou `Msg` não é `nil`.

## Marshal e Unmarshal em streaming

As interfaces [`io.Reader`](/pkg/io#Reader) e [`io.Writer`](/pkg/io#Writer) são onipresentes em Go, oferecendo acesso em streaming a recursos como conexões HTTP, WebSockets ou arquivos.
As funções `MarshalWrite` e `UnmarshalRead` permitem fazer marshal e unmarshal diretamente de e para esses streams, sem precisar de um `[]byte` intermediário que armazene a mensagem inteira.

```
func MarshalWrite(out io.Writer, in any, opts ...Options) (err error)
func UnmarshalRead(in io.Reader, out any, opts ...Options) (err error)
```

Por exemplo, podemos escrever a saída do marshal diretamente na saída padrão:

```
err := json.MarshalWrite(os.Stdout, m)
```

## Marshal e Unmarshal personalizados

Às vezes, o comportamento padrão de marshal não faz sentido para o seu tipo.

Por exemplo, suponha que temos um tipo que descreve a versão de um software.

```
type Version struct {
	Major, Minor, Patch int64
}

v := Version{1, 2, 3}
b, err := json.Marshal(s)
```

Isso faz o marshal como `{"Major":1,"Minor":2,"Patch":3}`, como esperado com base na definição da struct, mas uma string de versão como "1.2.3" provavelmente seria uma representação melhor para quem consome o JSON.

Implementando a interface [`MarshalerTo`](/pkg/encoding/json/v2#MarshalerTo), podemos fornecer uma representação JSON personalizada.
[`UnmarshalerFrom`](/pkg/encoding/json/v2#UnmarshalerFrom) faz o unmarshal da representação JSON personalizada.

```
type MarshalerTo interface {
	MarshalJSONTo(*jsontext.Encoder) error
}

type UnmarshalerFrom interface {
	UnmarshalJSONFrom(*jsontext.Decoder) error
}
```

Podemos implementar esses métodos para converter de e para representações em string.

```
func (v Version) MarshalJSONTo(enc *jsontext.Encoder) error {
	return json.MarshalEncode(enc, fmt.Sprintf("%d.%d.%d", v.Major, v.Minor, v.Patch))
}
```

Com o marshal personalizado, o valor `Version{1, 2, 3}` agora faz marshal como `"1.2.3"`.

```
func (v *Version) UnmarshalJSONFrom(dec *jsontext.Decoder) error {
	if k := dec.PeekKind(); k != jsontext.KindString {
		// Value must be a string.
		return &json.SemanticError{JSONKind: k}
	}

	var s string
	if err := json.UnmarshalDecode(dec, &s); err != nil {
		return err
	}

	_, err := fmt.Sscanf(s, "%d.%d.%d", &v.Major, &v.Minor, &v.Patch)
	return err
}
```

Com o unmarshal personalizado, `"1.2.3"` agora faz unmarshal como `Version{1, 2, 3}`.
Este exemplo simples exige exatamente o formato de versão `"major.minor.patch"`, mas um `UnmarshalJSONFrom` mais complexo poderia escolher adicionar flexibilidade, por exemplo tornando opcionais as versões minor e patch.

## Referências

Para mais informações, veja a documentação dos pacotes [encoding/json/v2](/pkg/encoding/json/v2) e [encoding/json/jsontext](/pkg/encoding/json/jsontext).

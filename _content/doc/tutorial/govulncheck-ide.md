<!--{
  "ia-translated": true,
  "Title": "Tutorial: Encontre e corrija dependências vulneráveis com o VS Code Go",
  "Breadcrumb": true
}-->

[Voltar para Segurança do Go](/security)

Você pode verificar seu código em busca de vulnerabilidades diretamente no editor, com a extensão Go para o Visual Studio Code.

Observação: para uma explicação sobre a correção de vulnerabilidade mostrada nas imagens abaixo, veja o [tutorial do govulncheck](/doc/tutorial/govulncheck).

## Pré-requisitos:

- **Go.** Recomendamos usar a versão mais recente do Go para acompanhar este tutorial. Para instruções de instalação, veja [Instalando o Go](/doc/install).
- **VS Code**, atualizado para a versão mais recente. [Baixe aqui](https://code.visualstudio.com/). Você também pode usar o Vim (veja [aqui](/security/vuln/editor#editor-specific-instructions) para detalhes), mas este tutorial foca no VS Code Go.
- **Extensão VS Code Go**, que pode ser [baixada aqui](https://marketplace.visualstudio.com/items?itemName=golang.go).
- **Alterações de configurações específicas do editor.** Você precisará modificar as configurações da sua IDE de acordo com [estas especificações](/security/vuln/editor#editor-specific-instructions) antes de conseguir reproduzir os resultados abaixo.


## Como buscar vulnerabilidades usando o VS Code Go

**Passo 1.** Execute "Go: Toggle Vulncheck"

O comando [Toggle Vulncheck](https://github.com/golang/vscode-go/wiki/Commands#go-toggle-vulncheck) exibe a análise de vulnerabilidades de todas as dependências listadas nos seus módulos. Para usar este comando, abra a [paleta de comandos](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) na sua IDE (Ctrl+Shift+P no Linux/Windows ou Cmd+Shift+P no macOS) e execute “Go: Toggle Vulncheck.” No seu arquivo go.mod, você verá os diagnósticos das dependências vulneráveis usadas tanto diretamente quanto indiretamente no seu código.

<div class="image">
  <center>
    <img style="width: 100%" width="2110" height="952" src="editor_tutorial_1.png" alt="Run Toggle Vulncheck"></img>
  </center>
</div>

Observação: para reproduzir este tutorial no seu próprio editor, copie o código abaixo para o seu arquivo main.go.

```
// This program takes language tags as command-line
// arguments and parses them.

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

Em seguida, certifique-se de que o arquivo go.mod correspondente ao programa fique assim:


```
module module1

go 1.18

require golang.org/x/text v0.3.5
```

Agora, execute `go mod tidy` para garantir que o seu arquivo go.sum seja atualizado.

**Passo 2.** Execute o govulncheck por meio de uma ação de código.

Executar o govulncheck usando uma ação de código permite que você foque nas dependências que são de fato chamadas no seu código. As ações de código no VS Code são marcadas por ícones de lâmpada; passe o mouse sobre a dependência relevante para ver informações sobre a vulnerabilidade e, em seguida, selecione “Quick Fix” para ver um menu de opções. Entre elas, escolha “run govulncheck to verify.” Isso vai retornar a saída relevante do govulncheck no seu terminal.

<div class="image">
  <center>
    <img style="width: 100%" width="2110" height="952" src="editor_tutorial_2.png" alt="govulncheck code action"></img>
  </center>
</div>

<div class="image">
  <center>
    <img style="width: 100%" width="2110" height="952" src="editor_tutorial_3.png" alt="VS Code Go govulncheck output"></img>
  </center>
</div>

**Passo 3**. Passe o mouse sobre uma dependência listada no seu arquivo go.mod.

A saída relevante do govulncheck sobre uma dependência específica também pode ser encontrada passando o mouse sobre a dependência no arquivo go.mod. Para uma consulta rápida às informações da dependência, essa opção é ainda mais eficiente do que usar uma ação de código.

<div class="image">
  <center>
    <img style="width: 100%" width="2110" height="952" src="editor_tutorial_4.png" alt="Hover over dependency for vulnerability information"></img>
  </center>
</div>

**Passo 4.** Atualize para uma versão “fixed in” da sua dependência.

Ações de código também podem ser usadas para atualizar rapidamente para uma versão da sua dependência em que a vulnerabilidade foi corrigida. Para fazer isso, selecione a opção “Upgrade” no menu suspenso de ações de código.

<div class="image">
  <center>
    <img style="width: 100%" width="2110" height="952" src="editor_tutorial_5.png" alt="Upgrade to Latest via code action menu"></img>
  </center>
</div>


## Recursos adicionais

- Veja [esta página](/security/vuln/editor) para mais informações sobre a verificação de vulnerabilidades na sua IDE. A seção [Notas e ressalvas](/security/vuln/editor#notes-and-caveats), em particular, discute casos especiais em que a verificação de vulnerabilidades pode ser mais complexa do que no exemplo acima.
- O [Go Vulnerability Database](https://pkg.go.dev/vuln/) reúne informações de muitas fontes existentes, além de relatos diretos feitos pelos mantenedores de pacotes Go à equipe de segurança do Go.
- A página [Go Vulnerability Management](/security/vuln/) oferece uma visão de alto nível da arquitetura do Go para detectar, reportar e gerenciar vulnerabilidades.

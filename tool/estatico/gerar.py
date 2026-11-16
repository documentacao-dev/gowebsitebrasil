#!/usr/bin/env python3
"""Gera a versão estática das páginas traduzidas para o Firebase Hosting.

O go.dev é servido por um programa em Go (cmd/golangorg) que monta as páginas
na hora. O Firebase Hosting só serve arquivos, então este script:

1. pede ao servidor local (já rodando em --servidor) cada página de _content/
   marcada com `ia-translated`, como se fosse o host go.dev em https (assim os
   links saem no formato de produção);
2. baixa o CSS, o JS, as imagens e as fontes que essas páginas usam
   (inclusive os url(...) de dentro do CSS);
3. grava tudo em --saida (padrão: public/).

Ficam de fora o Tour (app próprio em /tour/) e tudo que não foi traduzido: o
firebase.json manda os caminhos dinâmicos (/pkg, /dl, /play, /tour…) para o
go.dev e o 404.html leva qualquer outra página para a mesma página no go.dev.

Uso: go run ./cmd/golangorg -content=_content -http=localhost:6060 &
     python3 tool/estatico/gerar.py --servidor http://localhost:6060
"""
import argparse
import re
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / '_content'
MARCADOR = re.compile(r'ia-translated')
ASSET = re.compile(r'(?:href|src)="(/(?:css|js|images|fonts|favicon|static)[^"#?]*)')
CSS_URL = re.compile(r'url\(\s*[\'"]?([^\'")]+)')
HEADERS = {'Host': 'go.dev', 'X-Forwarded-Proto': 'https'}
SITE = 'https://go.documentacao.dev'
# Analytics do go.dev oficial (Google Tag Manager): não pode ir para o fork,
# senão os visitantes daqui viram dados na conta do Google.
GTM = [
    re.compile(r'<link rel="preconnect" href="https://www\.googletagmanager\.com">\s*'),
    re.compile(r'<script[^>]*>\(function\(w,d,s,l,i\).*?</script>\s*', re.S),
    re.compile(r'<noscript><iframe src="https://www\.googletagmanager\.com/.*?</noscript>\s*', re.S),
    re.compile(r'<meta class="js-gtmID"[^>]*>\s*'),  # o JS do pkgsite lê o ID daqui
    re.compile(r'<script>\s*// this will throw if the querySelector.*?</script>\s*', re.S),
    re.compile(r'<noscript>\s*<iframe src="https://www\.googletagmanager\.com/.*?</noscript>\s*', re.S),
    re.compile(r'<section class="Cookie-notice js-cookieNotice">.*?</section>\s*', re.S),
]


def limpar(html):
    for rx in GTM:
        html = rx.sub('', html)
    # A página canônica é a traduzida, não a do go.dev em inglês.
    html = re.sub(r'(<link rel="canonical" href=")https://go\.dev', r'\1' + SITE, html)
    html = re.sub(r'(<meta name="og:url" content=")https://go\.dev', r'\1' + SITE, html)
    return html
FORA = ('tour/',)  # app Angular próprio, não dá para espelhar como página


def baixar(servidor, caminho):
    req = urllib.request.Request(servidor + caminho, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return r.read()


def paginas():
    """URL e arquivo de saída de cada página traduzida."""
    for p in sorted(CONTENT.rglob('*')):
        if p.suffix not in ('.md', '.html') or not p.is_file():
            continue
        rel = p.relative_to(CONTENT)
        if str(rel).startswith(FORA) or not MARCADOR.search(p.read_text(errors='ignore')[:600]):
            continue
        sem = rel.with_suffix('')
        if sem.name == 'index':
            url = '/' if str(sem.parent) == '.' else '/' + str(sem.parent) + '/'
            saida = sem.parent / 'index.html'
        else:
            url = '/' + str(sem)
            saida = sem.with_suffix('.html')
        yield url, saida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--servidor', default='http://localhost:6060')
    ap.add_argument('--saida', default=str(ROOT / 'public'))
    a = ap.parse_args()
    out = Path(a.saida)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)

    pendentes, n, falhas = set(), 0, []
    for url, saida in paginas():
        try:
            html = baixar(a.servidor, url).decode()
        except Exception as e:  # página que o servidor não serve nesse caminho
            falhas.append(f'{url}: {e}')
            continue
        html = limpar(html.replace('<html lang="en">', '<html lang="pt-BR">'))
        (out / saida).parent.mkdir(parents=True, exist_ok=True)
        (out / saida).write_text(html)
        pendentes |= set(ASSET.findall(html))
        n += 1

    feitos = set()
    while pendentes:
        caminho = pendentes.pop()
        if caminho in feitos or '.' not in caminho.rsplit('/', 1)[-1]:
            continue
        feitos.add(caminho)
        try:
            dados = baixar(a.servidor, caminho)
        except Exception:
            try:  # arquivo que só existe em produção (ex.: /static/ do pkgsite)
                with urllib.request.urlopen('https://go.dev' + caminho) as r:
                    dados = r.read()
            except Exception as e:
                print(f'aviso: {caminho}: {e}')
                continue
        destino = out / caminho.lstrip('/')
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(dados)
        if caminho.endswith('.css'):
            for ref in CSS_URL.findall(dados.decode(errors='ignore')):
                if ref.startswith('data:'):
                    continue
                alvo = urlparse(urljoin(caminho, ref)).path
                if alvo.startswith('/'):
                    pendentes.add(alvo)

    for extra in ('404.html', 'robots.txt'):
        shutil.copy(Path(__file__).parent / extra, out / extra)
    for f in falhas:
        print('aviso: página não gerada', f)
    print(f'{n} páginas e {len(feitos)} arquivos de apoio em {out}')


if __name__ == '__main__':
    main()

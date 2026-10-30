# copywriting-mestre

Skill de copywriting de alta conversão, baseada nas estratégias e nos estilos dos maiores copywriters da história. Ela define a estrutura de comunicação mais eficaz para cada público, considerando dores, desejos, nível de consciência e objetivo.

## O que ela faz

1. **Mapeamento cirúrgico.** Antes de escrever, analisa o contexto e faz de 2 a 4 perguntas essenciais (público, dor, canal, oferta) só se faltar informação.
2. **Entrega multi-ângulo.** Sempre 3 a 4 variações com lógicas psicológicas distintas: PAS (dor), BAB (transformação), quebra de objeção e urgência/ação imediata.
3. **Reorganização de estudos.** Sintetiza briefs, relatórios e pesquisas em Dores Principais, Desejos Ocultos, Objeções e UVP.
4. **Tom de alta conversão.** Linguagem direta, verbos de ação, sem jargão genérico e sem alegações que não tenham prova.
5. **Voz dos mestres.** Aplica técnicas de 17 copywriters históricos e de 3 autores de fórmulas (perfis em `skills/copywriter-mestre/references/mestres/`).

Serve para headlines, copy de vendas, páginas de produto e landing pages, anúncios, e-mails, CTAs e microcopy.

## Instalação rápida

Requisito: um assistente de IA que leia skills no formato `SKILL.md`. Os instaladores copiam a pasta `skills/copywriter-mestre` para o seu computador; não instalam dependências nem alteram outras configurações.

### macOS, Linux e WSL

Sem baixar nada antes (uma linha):

```bash
curl -fsSL https://raw.githubusercontent.com/andreischuaste12-ctrl/copywriting-mestre/main/install.sh | bash
```

Ou, com o repositório baixado (clone ou ZIP):

```bash
git clone https://github.com/andreischuaste12-ctrl/copywriting-mestre.git
cd copywriting-mestre
./install.sh
```

### Windows (PowerShell)

1. Baixe o repositório: no GitHub, **Code → Download ZIP**, e extraia (ou use `git clone`).
2. Abra o PowerShell na pasta extraída.
3. Rode:

```powershell
.\install.ps1
```

Se o Windows bloquear scripts, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### Instalação manual

Copie a pasta `skills/copywriter-mestre` inteira (com `SKILL.md` e `references/`) para a pasta de skills do seu assistente. Consulte a documentação dele para saber o caminho. O arquivo `SKILL.md` precisa ficar diretamente dentro de uma pasta chamada `copywriter-mestre`.

## Opções do instalador

| Objetivo | macOS / Linux / WSL | Windows |
|---|---|---|
| Instalar para o seu usuário (padrão) | `./install.sh` | `.\install.ps1` |
| Instalar só em uma pasta | `./install.sh --dest PASTA` | `.\install.ps1 -Dest "C:\PASTA"` |
| Instalar só no projeto atual | `./install.sh --project` | `.\install.ps1 -Project` |
| Simular sem alterar nada | `./install.sh --dry-run` | `.\install.ps1 -DryRun` |
| Remover | `./install.sh --uninstall` | `.\install.ps1 -Uninstall` |

As pastas padrão estão listadas no início de cada script (`DEFAULT_SUBDIRS` / `$DefaultSubdirs`). Para outro assistente ou outra pasta, use `--dest` / `-Dest`.

Segurança do instalador: ele só substitui ou remove uma pasta `copywriter-mestre` que contenha um `SKILL.md` com `name: copywriter-mestre`. Se encontrar outra coisa com esse nome, para e avisa.

## Verificar a instalação

1. Confirme que o arquivo existe em `<pasta de skills>/copywriter-mestre/SKILL.md`.
2. Reinicie o assistente (ou abra uma nova sessão).
3. Peça algo como: *"Escreva headlines para um tênis de corrida, público de iniciantes."* A skill deve fazer 2–4 perguntas, ou declarar suas suposições, e depois entregar 3–4 variações.

## Como usar

| Quero… | Exemplo de pedido |
|---|---|
| Headlines e anúncios | "Crie anúncios para Meta Ads do meu curso de Excel, público de analistas júnior." |
| E-mail de venda | "Escreva um e-mail de carrinho abandonado para uma loja de cafés especiais." |
| Página de produto ou LP | "Estruture a landing page do meu serviço de contabilidade para MEI." |
| Organizar um estudo | "Resuma este relatório de pesquisa em dores, desejos, objeções e UVP." *(cole o texto)* |
| Estilo de um mestre | "Reescreva este e-mail com a conversa direta de Halbert." |

Dica: quanto mais contexto você der (público, produto, preço, prova, canal), menos perguntas ela precisa fazer.

## Atualizar e remover

- **Atualizar:** baixe a versão nova do repositório (`git pull` ou novo ZIP) e rode o instalador de novo. Ele substitui a versão anterior.
- **Remover:** rode o instalador com `--uninstall` / `-Uninstall`.

## Problemas comuns

| Sintoma | Causa provável e solução |
|---|---|
| A skill não aparece | O assistente não foi reiniciado, ou a pasta de skills é outra: use `--dest` / `-Dest`. |
| `Recusado: ... não parece ser esta skill` | Já existe uma pasta com esse nome e outro conteúdo. Mova-a e rode de novo. |
| `curl` ou `tar` não encontrado | Instale-os, ou baixe o ZIP do repositório e rode `./install.sh`. |
| PowerShell: script bloqueado | Use `powershell -ExecutionPolicy Bypass -File .\install.ps1`. |
| Falha de rede ao baixar | Baixe o ZIP pelo navegador e rode o instalador local. |

## Estrutura

```
install.sh · install.ps1          instaladores
LICENSE · NOTICE                  licença Apache-2.0 e avisos
skills/copywriter-mestre/
├── SKILL.md                      instruções da skill
└── references/
    ├── guia-copywriting.md       guia: estratégia, estruturas, canais, testes
    ├── fontes.md                 todos os links e o que cada um sustenta
    └── mestres/                  17 mestres + 3 autores de fórmulas
```

## Licença

Distribuído sob a [Apache License 2.0](LICENSE). Você pode usar, copiar, modificar e distribuir, inclusive comercialmente, mantendo o aviso de copyright e a licença. O software é fornecido sem garantias. Nomes, obras, campanhas e marcas citados nas referências pertencem a seus titulares e aparecem só para identificação e referência histórica (veja [NOTICE](NOTICE)).

Copyright 2026 Andrei.

# Comece em 15 minutos

Este roteiro usa dados fictícios e roda localmente. Não exige chave de API. Ele demonstra o fluxo de revisão; não mede desempenho de um modelo.

## 1. Prepare o ambiente

Na raiz do repositório, com Python 3.10 ou superior, ative seu ambiente virtual e execute:

```sh
python -m pip install -r requirements-validation.txt
python tools/copywriter.py init --example pt-BR --dest ./meu-primeiro-caso
```

O comando cria `brief.json` e `output.json` em uma pasta nova. Uma pasta existente é preservada. O brief contém público, oferta, CTA e condições; o output contém uma proposta de texto. Para o exemplo em inglês, use `--example en-US` e outra pasta.

## 2. Valide a primeira proposta

```sh
python tools/copywriter.py validate --brief ./meu-primeiro-caso/brief.json --draft ./meu-primeiro-caso/output.json --format markdown
```

Resultado esperado: verificações automáticas aprovadas e revisão humana pendente. Leia a oferta, confira as fontes e valide o significado e as permissões. O comando não gera nem corrige texto automaticamente.

## 3. Veja um bloqueio

Edite **somente o output**, trocando `R$ 49` por `R$ 29`, e execute novamente. Resultado esperado: bloqueio por condição obrigatória alterada e número não fornecido. Restaure o preço do brief; não altere o brief só para aprovar a saída.

Erros típicos: CTA diferente do destino → `cta_mismatch`; condição omitida → `required_phrase`; promessa cadastrada sem fonte → `claim_without_source`; permissão pendente → `authorization_pending`. Cada achado inclui prioridade, categoria e orientação de correção.

## 4. Revise casos de outros setores

```sh
python tools/copywriter.py batch --manifest examples/sectors/batch.json --out-dir ./relatorios-setores
```

Os seis cenários abrangem SaaS/B2B, e-commerce, educação, fintech, saúde e serviços/SMS, com textos em português, inglês e espanhol. Todos são sintéticos. Os exemplos de saúde/finanças continuam exigindo análise especializada mesmo quando passam nas regras literais.

## 5. Registre eventos se precisar

Adicione `--log ./events.jsonl` explicitamente a uma validação. Consulte o resumo com:

```sh
python tools/copywriter.py summary --log ./events.jsonl --format markdown
```

Sem `--log`, nada é registrado. Veja [observabilidade](OBSERVABILITY.md) para campos, limites e taxas. Para uso em assistentes, consulte a [matriz de compatibilidade](COMPATIBILITY.md); copiar uma pasta não comprova que um modelo carregou ou seguiu a skill.

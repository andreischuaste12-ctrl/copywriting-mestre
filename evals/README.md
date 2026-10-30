# Avaliação da skill

`evals.json` reúne os 4 pedidos de teste, as assertions e 7 consultas de disparo (4 devem acionar a skill, 3 não).

## Como repetir

Instale a skill em uma pasta de teste, rode cada pedido com e sem a skill em sessões independentes e compare com as assertions. Rode cada pedido mais de uma vez: a saída varia.

## Resultado da checagem de out/2026 (1 execução por pedido, assertions verificadas por script e leitura)

| | com skill | sem skill |
|---|---|---|
| Assertions atendidas | 12 de 13 | 7 de 13 |
| Disparo (consultas) | 7 de 7 corretas | n/a |

A assertion que falhou com a skill (acrescentar "mais de" a 2.300 avaliações) levou a uma regra de fidelidade ao briefing. Depois dela, 4 de 4 novas execuções do pedido 2 saíram sem o problema.

## Limites

- Amostra pequena (4 pedidos, 1 a 4 execuções); a saída de um modelo varia entre execuções.
- Assertions e skill foram escritas pela mesma pessoa/sistema; não há avaliação cega nem humana.
- Mede estrutura e honestidade das alegações. **Não mede conversão real**: só teste A/B com tráfego mede isso.

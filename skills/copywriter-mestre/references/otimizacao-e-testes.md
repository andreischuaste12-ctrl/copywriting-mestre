# Otimização e testes

Use ao propor testes, ler resultados ou diagnosticar por que uma peça não converte. Complementa a seção 5 do `guia-copywriting.md`.

## 1. Ciclo de otimização

1. **Diagnóstico:** qual barreira observada motiva a mudança (relevância, compreensão, prova, confiança, conveniência)?
2. **Hipótese:** "Se [mudança], então [comportamento] porque [barreira]." Uma hipótese por teste.
3. **Métrica primária + proteções (guardrails):** conversão, margem, devolução, cancelamento, qualidade do lead, reclamações. CTR sozinho engana.
4. **Dimensione antes de rodar:** calcule o tamanho de amostra necessário para o efeito mínimo que importa ao negócio (calculadora de Evan Miller). Defina duração em ciclos completos (semanas inteiras).
5. **Rode sem "espiar":** parar no primeiro resultado "significativo" infla falsos positivos. Defina o critério de parada antes.
6. **Cheque a divisão de tráfego (SRM):** compare contagens observadas e esperadas com o teste de SRM da plataforma ou um teste estatístico apropriado, sob um critério definido antes da análise. Uma diferença percentual isolada não demonstra falha: flutuações aleatórias dependem do tamanho da amostra. Um alerta estatístico indica possível problema de qualidade, não identifica sua causa. Suspenda a interpretação do efeito até investigar atribuição, coleta, filtros e segmentação; não use um limiar universal sem justificativa (Kohavi et al.).
7. **Leia o efeito, não só o p-valor:** tamanho do efeito, intervalo e impacto em dinheiro. Um teste informa a decisão naquele contexto; não valida uma fórmula para sempre.
8. **Registre o aprendizado:** hipótese, resultado, limite e próxima pergunta.

## 2. Tráfego baixo

Com poucas conversões, teste A/B clássico não detecta efeitos pequenos. Alternativas: testar mudanças grandes (ângulos distintos A–D, não troca de palavra), usar métricas intermediárias com cuidado, combinar com entrevistas e leitura de atendimento/avaliações, e comparar antes/depois só com ressalvas de sazonalidade e mix de canal.

## 3. Como priorizar o que testar

Não há uma ordem universal de alavancas. Priorize o gargalo observado, impacto esperado, confiança na evidência e esforço para intervir. Mudanças em oferta, preço, condições ou garantia são decisões de negócio: proponha-as como opções e não suponha autorização ou disponibilidade.

## 4. Mapa de forças de decisão (útil no modo estudo)

Modelo de Jobs to Be Done aplicado a vendas (Moesta): a troca acontece quando **push + pull superam anxiety + hábito**.

| Força | Pergunta | Onde entra na copy |
|---|---|---|
| **Push** | O que incomoda na situação atual? | dores → ângulo A |
| **Pull** | O que atrai na nova solução? | desejos/transformação → ângulo B |
| **Ansiedade** | O que dá medo ou dúvida ao trocar? | objeções → ângulo C |
| **Hábito** | Por que continuar como está é confortável? | custo de esperar, facilidade da troca → ângulo D |

Reduzir ansiedade e hábito costuma render mais do que aumentar a promessa (opinião de praticantes, não resultado universal).

## 5. Escrita para a web e checkout

- **Leitura por varredura:** estudos de Nielsen e Morkes (1997) encontraram que a maioria dos usuários escaneia páginas e que texto conciso, escaneável e objetivo teve melhor usabilidade que texto promocional. Amostras pequenas e antigas: use como direção (subtítulos informativos, blocos curtos, menos adjetivo), não como percentual a citar.
- **Checkout:** custos inesperados (frete, impostos, taxas) lideram os motivos de abandono citados pela Baymard. Os percentuais variam entre levantamentos; não cite número sem ler a fonte. Ação prática: mostrar preço total, prazo e condições antes da decisão (também exigência de transparência, ver `conformidade-br.md`).

## 6. Hipóteses de intervenção por barreira

Os sinais abaixo não isolam causa. Use-os para formular hipóteses e procure evidência adicional — por exemplo, gravações de erro, termos de busca, objeções no atendimento, teste de compreensão, preço, frete, estoque, usabilidade ou falha de pagamento — antes de escolher uma intervenção.

| Barreira possível | Sinal que pode motivar investigação | Hipótese de intervenção |
|---|---|---|
| Relevância | cliques baixos, rejeição alta | gancho mais específico ao segmento; headline com a linguagem do público |
| Compreensão | rolagem sem ação ou dúvidas recorrentes | explicar "o que é, para quem, como funciona" em 1–2 frases e demonstrar |
| Prova | leitura sem compra | testar evidência compatível com a alegação, após investigar preço e adequação |
| Confiança | abandono no checkout/formulário | verificar termos, política, reputação e falhas funcionais antes de alterar a mensagem |
| Conveniência | abandono em etapas | investigar fricção, campos, custo total, estoque e pagamento antes de simplificar o texto |

## Fontes

- Miller, Evan. [How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html)
- Kohavi, Tang, Xu. *Trustworthy Online Controlled Experiments* (Cambridge, 2020), cap. "Sample Ratio Mismatch and Other Trust-Related Guardrail Metrics": [Cambridge](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/sample-ratio-mismatch-and-other-trustrelated-guardrail-metrics/8DBB0F59AC7729D7BC6B94690DB9CCD5)
- Moesta, Bob; Engle, Greg. *Demand-Side Sales 101* (forças de push, pull, ansiedade e hábito). Fonte conferida apenas por resumos; leia o livro antes de citar frases.
- Morkes, J.; Nielsen, J. "Concise, SCANNABLE, and Objective: How to Write for the Web" (1997) e Nielsen, "How Users Read on the Web" (1997). Conferidos por resumos secundários.
- [Baymard Institute — cart abandonment](https://www.baymard.com/blog/cart-abandonment) e [reduce cart abandonment](https://baymard.com/blog/reduce-cart-abandonment)

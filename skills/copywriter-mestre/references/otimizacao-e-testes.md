# Otimização e testes

Use ao propor testes, ler resultados ou diagnosticar por que uma peça não converte. Complementa a seção 5 do `guia-copywriting.md`.

## 1. Ciclo de otimização

1. **Diagnóstico:** qual barreira observada motiva a mudança (relevância, compreensão, prova, confiança, conveniência)?
2. **Hipótese:** "Se [mudança], então [comportamento] porque [barreira]." Uma hipótese por teste.
3. **Métrica primária + proteções (guardrails):** conversão, margem, devolução, cancelamento, qualidade do lead, reclamações. CTR sozinho engana.
4. **Dimensione antes de rodar:** calcule o tamanho de amostra necessário para o efeito mínimo que importa ao negócio (calculadora de Evan Miller). Defina duração em ciclos completos (semanas inteiras).
5. **Rode sem "espiar":** parar no primeiro resultado "significativo" infla falsos positivos. Defina o critério de parada antes.
6. **Cheque a divisão de tráfego (SRM):** se a proporção real entre variações diverge da planejada, há erro de aleatorização ou de medição e o resultado não é confiável (Kohavi et al.).
7. **Leia o efeito, não só o p-valor:** tamanho do efeito, intervalo e impacto em dinheiro. Um teste informa a decisão naquele contexto; não valida uma fórmula para sempre.
8. **Registre o aprendizado:** hipótese, resultado, limite e próxima pergunta.

## 2. Tráfego baixo

Com poucas conversões, teste A/B clássico não detecta efeitos pequenos. Alternativas: testar mudanças grandes (ângulos distintos A–D, não troca de palavra), usar métricas intermediárias com cuidado, combinar com entrevistas e leitura de atendimento/avaliações, e comparar antes/depois só com ressalvas de sazonalidade e mix de canal.

## 3. O que testar primeiro (maior alavanca, em ordem)

1. Oferta, preço, condições e garantia (o que é dito).
2. Ângulo da mensagem: dor, transformação, objeção, ação.
3. Prova e clareza da promessa na primeira dobra.
4. Headline e CTA.
5. Detalhes de formato (ordem de blocos, tamanho, imagem).

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

## 6. Intervenção típica por barreira

| Barreira | Sinal comum | Intervenção de copy |
|---|---|---|
| Relevância | cliques baixos, rejeição alta | gancho mais específico ao segmento; headline com a linguagem do público |
| Compreensão | rolagem sem ação, dúvidas repetidas no atendimento | explicar "o que é, para quem, como funciona" em 1–2 frases e demonstração |
| Prova | leem mas não clicam em comprar | evidência compatível com a alegação (demonstração, avaliações reais, dados contextualizados) |
| Confiança | abandono no checkout/formulário | garantia, política de troca, dados da empresa, termos claros |
| Conveniência | abandono em etapas | menos campos, CTA que diz o que acontece depois, preço total visível |

## Fontes

- Miller, Evan. [How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html)
- Kohavi, Tang, Xu. *Trustworthy Online Controlled Experiments* (Cambridge, 2020), cap. "Sample Ratio Mismatch and Other Trust-Related Guardrail Metrics": [Cambridge](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/sample-ratio-mismatch-and-other-trustrelated-guardrail-metrics/8DBB0F59AC7729D7BC6B94690DB9CCD5)
- Moesta, Bob; Engle, Greg. *Demand-Side Sales 101* (forças de push, pull, ansiedade e hábito). Fonte conferida apenas por resumos; leia o livro antes de citar frases.
- Morkes, J.; Nielsen, J. "Concise, SCANNABLE, and Objective: How to Write for the Web" (1997) e Nielsen, "How Users Read on the Web" (1997). Conferidos por resumos secundários.
- [Baymard Institute — cart abandonment](https://www.baymard.com/blog/cart-abandonment) e [reduce cart abandonment](https://baymard.com/blog/reduce-cart-abandonment)

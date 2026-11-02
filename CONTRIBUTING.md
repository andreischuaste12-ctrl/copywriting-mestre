# Como contribuir / How to contribute

Contribuições são bem-vindas: correções, documentação, exemplos, melhorias nas instruções, testes e relatos de problemas. Você pode escrever em português ou inglês. Se estiver começando, uma issue com uma ideia ou dúvida já ajuda.

## Antes de começar

1. Pesquise as issues e pull requests existentes para evitar trabalho duplicado. Para mudanças grandes, abra uma issue descrevendo o problema e a proposta antes de implementá-la.
2. Não inclua dados pessoais, credenciais ou informações confidenciais em exemplos, logs ou relatos. Use dados sintéticos.
3. Envie apenas material que você tem direito de compartilhar. Contribuições ao repositório são disponibilizadas sob a [licença Apache 2.0](LICENSE); preserve os avisos de atribuição aplicáveis.

## Enviar uma alteração

1. Faça um fork do repositório, clone-o e crie uma branch para sua mudança.
2. Faça uma alteração focada e atualize documentação e exemplos quando necessário. Para mudanças no comportamento da skill, considere os casos de avaliação em [evaluation/README.md](evaluation/README.md); testes automatizados não comprovam o comportamento de um modelo.
3. Para executar as verificações locais (Python 3.10+):

   ```sh
   python -m pip install -r requirements-validation.txt -r requirements-dev.txt
   python tools/release.py check
   python -m unittest discover -s tests -v
   ruff check . && mypy
   ```

   Ao adicionar ou mover uma referência, registre-a em `skills/copywriter-master/references/registry.json` e rode `python tools/references.py index` (ver [arquitetura](docs/ARCHITECTURE.md)). Em macOS, Linux ou WSL, execute também `bash -n install.sh`. O CI verifica outras plataformas e o instalador PowerShell.
4. Abra um pull request descrevendo o problema, a solução, como foi verificada e eventuais limitações. Vincule a issue relacionada, se houver. Se alguma verificação não puder ser executada, informe isso no PR.

Para relatar um problema, informe o comportamento esperado e o observado, passos para reproduzir, ambiente e exemplos sem dados sensíveis. Para propor uma melhoria, explique a necessidade e o resultado desejado. Não publique vulnerabilidades ou segredos em issues públicas.

## English

Contributions are welcome, including bug reports, documentation, examples, skill instructions, and tests. Please follow the steps above: check existing issues, discuss substantial changes first, use synthetic data, run the checks, and describe your changes and verification in a pull request. You may write in English or Portuguese. Submissions are made available under the [Apache 2.0 license](LICENSE); retain applicable attribution notices.

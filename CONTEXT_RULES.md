# Regras de contexto — TaskAnalyzer

Regras transpostas da especificação da fase 1 para orientar a implementação e a revisão humana.

## Diretrizes obrigatórias

- Usar Python 3.11 ou superior, PEP 8 e type hints em todas as funções e parâmetros.
- Escrever funções pequenas, coesas e com uma responsabilidade; usar nomes descritivos.
- Documentar a interface pública no padrão Google Style.
- Tratar erros com exceções específicas e mensagens claras. Usar `logging` somente se houver evento relevante a registrar.
- Produzir resultados determinísticos e manter consistência entre contrato, código e testes.
- Considerar apenas tarefas concluídas válidas nas métricas de duração e atraso.
- Calcular duração por `data_conclusao - data_inicio` e atraso por `data_conclusao > prazo`.
- Usar datas UTC e arredondar durações e percentuais para duas casas decimais.
- Organizar os indicadores por `baixa`, `media` e `alta`.

## Restrições

- Não adicionar bibliotecas externas além das autorizadas em `requirements.txt`.
- Não mudar a estrutura do projeto, os cenários de aceite ou a interface pública sem atualizar o contrato e obter autorização.
- Não persistir dados, inventar requisitos, esconder erros previstos ou acrescentar funcionalidades sem autorização.
- Não modificar requisitos para facilitar a implementação.

## Aplicação nesta fase

O contrato versionado em `specs/task_analyzer_spec.md` é a referência do código. O enunciado da fase 2 altera explicitamente duas decisões da fase 1: pede duração também em horas e médias `0.0` quando não há tarefas concluídas válidas. Essas alterações estão registradas na seção **Ajustes da fase 2** da especificação, para que implementação e testes tenham uma única regra verificável.

Antes da homologação, executar os testes, revisar tipos, métricas, casos de borda e erros contra a especificação. A aprovação final do trabalho cabe ao estudante.

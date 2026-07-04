# Roadmap — TDD Orchestrator

## Objetivo final
Sistema capaz de desenvolver software em múltiplas linguagens usando agentes de IA especializados, com aprovação humana obrigatória em cada etapa.

**Linguagens alvo:** Python e Flutter (Dart). Outras linguagens podem ser adicionadas após a estrutura estar pronta.

## Estratégia de versionamento

```
main     — versão estável, sempre funcional
dev      — próxima versão em desenvolvimento
feature/ — uma branch por etapa, criada a partir de dev
```

Merge de feature → dev quando a etapa estiver testada.
Merge de dev → main quando o conjunto estiver estável.

## Etapas

### Etapa 1 — Executor polimórfico (~4 dias)
**Branch:** `feature/executor-polimorfico`

- `test_runner.py` vira um dispatcher por linguagem
- Python → `pytest`
- Flutter → `flutter test`
- Parser de falhas adaptado para cada formato de saída
- Agentes recebem a linguagem como contexto nos prompts

### Etapa 2 — Múltiplos arquivos Python (~4 dias)
**Branch:** `feature/multiplos-arquivos`

- Generalizar o orquestrador para iterar sobre múltiplos módulos
- Agente de Arquitetura produz documento JSON com módulos e interfaces
- Orquestrador hierárquico: loop por módulo dentro do ciclo TDD

### Etapa 3 — Suporte Flutter (~12 dias)
**Branch:** `feature/flutter`

- Instalação e configuração do Flutter SDK
- Estrutura de projeto Flutter no `workspace/` (`pubspec.yaml`, `lib/`, `test/`)
- Prompts específicos para Dart/Flutter
- Executor para `flutter test`

### Buffer para ajustes (~4 dias)

## Estimativa total
~24 dias corridos a partir de 24/06/2026 → previsão: **18 de julho de 2026**

## Adicionando novas linguagens (após estrutura pronta)

| Tipo | Exemplos | Estimativa |
|---|---|---|
| Arquivo único, executor direto | Ruby, Go, Rust | ~4 dias |
| Estrutura de projeto | Java, Node.js, C# | ~4-8 dias |
| Ambiente complexo | Swift/iOS, Kotlin/Android | ~8-12 dias |

## Próximas evoluções consideradas (não priorizadas)

- **Skills:** modelo chama funções externas (ex: calculadora) em vez de estimar valores
- **RAG:** injeta requisitos anteriores similares e documentação técnica no contexto
- **Agente de Arquitetura:** decompõe requisitos de sistema em módulos com interfaces
- **Interface web:** substituir aprovação via terminal por diff visual no browser
- **Testes de integração:** fase final verificando módulos em conjunto

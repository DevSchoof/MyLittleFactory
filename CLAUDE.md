# Orquestrador de TDD com agentes de IA

## O que é este projeto

Sistema que automatiza parte do ciclo de TDD (Test-Driven Development)
usando três agentes de IA especializados, rodando sobre um LLM local
via RamaLama (https://github.com/containers/ramalama), com aprovação
humana obrigatória em cada etapa.

Contexto: projeto de portfólio de transição de carreira para
desenvolvimento de software, com foco em IA aplicada, infraestrutura
local de LLM e boas práticas de engenharia (TDD, separação de papéis,
validação independente).

## Por que três agentes, e não um só

Se o mesmo agente escreve o teste e o código que passa nele, ele pode
"satisfazer" o teste de forma superficial sem resolver o problema real.
Por isso o Agente de Validação nunca tem acesso aos testes originais —
só ao requisito em linguagem natural e ao código final. Isso simula um
processo de QA independente. Esse isolamento é uma decisão de design
intencional e não deve ser "simplificado" sem discutir antes.

## Arquitetura (fluxo)

```
Humano define requisito
    -> Agente de Testes (RED)        gera testes que devem falhar
    -> [aprovação humana]
    -> Agente de Código (GREEN)      implementa até passar nos testes reais (pytest)
    -> [aprovação humana]
    -> Agente de Validação           cria testes NOVOS e independentes
    -> se reprovar, volta para o Agente de Código com o motivo da falha
```

Nenhuma transição de fase é decidida pela opinião do modelo — a fase
GREEN só avança quando o `pytest` real confirma que os testes passam.

## Stack

- Python 3
- `requests` para falar com a API local do RamaLama (compatível com OpenAI)
- `pytest` como executor de teste real
- Sem framework de agentes (LangChain, CrewAI etc.) de propósito — o
  orquestrador é uma máquina de estados simples em `orchestrator.py`.
  Só considerar framework externo se a complexidade justificar.

## Arquivos principais

| Arquivo | Responsabilidade |
|---|---|
| `llm_client.py` | Cliente HTTP para `http://localhost:8080/v1` (RamaLama serve) |
| `agents.py` | TestAgent, CodeAgent, ValidationAgent |
| `test_runner.py` | Escreve arquivos no `workspace/` e roda pytest de verdade |
| `cli.py` | Checkpoint de aprovação humana via terminal |
| `orchestrator.py` | Máquina de estados (`Estado` enum) que conecta tudo |
| `main.py` | Ponto de entrada |
| `prompts/*.txt` | System prompt de cada agente — editar aqui, não hardcoded no código |

## Como rodar

1. Subir o modelo local: `ramalama serve gemma3:4b`
2. `pip install -r requirements.txt --break-system-packages`
3. `python main.py`

Hardware de referência: GPU AMD RX 7600 (8GB VRAM), 16GB RAM. Modelos
ficam na faixa de 4B-7B com quantização Q4 — não sugerir modelos maiores
sem confirmar antes que o hardware mudou.

## Limitações conhecidas (próximos passos naturais)

- Só lida com uma função por vez (sem múltiplos arquivos/módulos)
- Sem rollback automático entre tentativas de código (considerar git)
- Aprovação humana só via terminal — interface web é evolução natural
- Sem log estruturado persistente das decisões ainda

## Regras de trabalho

- Não remover os checkpoints de aprovação humana sem que eu peça
  explicitamente — é o ponto central do design.
- Não dar ao Agente de Validação acesso aos testes do Agente de Testes
  em nenhuma refatoração futura — quebraria a independência da validação.
- Ao alterar prompts em `prompts/`, manter a regra de "responda apenas
  com o código, sem explicações" — isso evita ter que fazer parsing
  de texto extra na resposta do modelo.

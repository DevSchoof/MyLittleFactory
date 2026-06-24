"""
Cliente simples para falar com o endpoint local do RamaLama
(`ramalama serve <modelo>`), que expõe uma API compatível com a OpenAI.

Trocar de modelo local para outro endpoint (ou para a API real da OpenAI)
exige só mudar BASE_URL e, se necessário, adicionar uma chave de API.
"""

import requests

BASE_URL = "http://localhost:8080/v1"
DEFAULT_MODEL = "local-model"  # nome interno usado pelo RamaLama, ajuste se necessário
TIMEOUT_SECONDS = 120


class LLMClient:
    def __init__(self, base_url: str = BASE_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url
        self.model = model

    def chat(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> str:
        """
        Envia uma conversa de 2 mensagens (system + user) e retorna o texto
        de resposta do modelo. Temperatura baixa por padrão: queremos respostas
        consistentes (testes e código), não criatividade.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

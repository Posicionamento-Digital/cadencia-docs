---
date: 2026-05-14
tags: [processos, ia, audio, tts, elevenlabs, openai, n8n, tecnologia, automacao]
moc: "[[MOC-Inbox]]"
---
# Prompts para Áudio — TTS (Text-to-Speech)

Configurações e boas práticas para síntese de voz em português brasileiro.

---

## Configurações de TTS

**Idioma:** `pt-BR` (padrão BCP-47)
- `pt` = Código ISO 639-1 para português
- `BR` = Código ISO 3166-1 alpha-2 para Brasil

**Velocidade ideal:** `0.95` a `1.05`
- `0.95` → Calma e clareza, ideal para públicos menos técnicos
- `1.0` → Padrão, funciona para a maioria dos casos
- `1.05` → Mais energia, útil para CTAs e benefícios

**Evitar:**
- Abaixo de `0.9` → Fala arrastada
- Acima de `1.2` → Soa artificial

---

## API OpenAI (TTS)

```python
response = openai.audio.speech.create(
    model="tts-1",        # ou "tts-1-hd" para alta definição
    voice="nova",         # ou "alloy", "echo", "fable", "onyx", "shimmer"
    input="Texto a converter em áudio.",
    language="pt-BR"      # Idioma e região
)
```

**Vozes recomendadas para pt-BR:**
- `nova` → Tom mais fluido e natural
- `shimmer` → Tom suave, adequado para consultivo

As vozes são multilíngues — o parâmetro `language="pt-BR"` melhora pronúncia e entonação.

---

## Implementação no N8N

```json
{
  "model": "tts-1-hd",
  "input": "{{ $json.texto }}",
  "voice": "nova",
  "speed": 1.0
}
```

---

## ElevenLabs — Configurações Adicionais

- **Velocidade de Fala:** 0.9 (ligeiramente mais lento para clareza)
- **Ênfase em Palavras-Chave:** Aplicar stress vocal em "economizar", "automático", "solução"
- **Voz Recomendada:** Tom masculino, adulto, calmo e confiante (ex.: "Voz João - Estilo Consultivo")

---

## Dicas de Qualidade

1. **Combine com a voz certa:** `nova` ou `shimmer` para pt-BR (tons mais fluidos)
2. **Teste com amostras:** Grave com `0.95`, `1.0` e `1.05` e valide com usuários reais
3. **Evite extremos:** Valores fora do range `0.9-1.1` comprometem a naturalidade

---

## Notas Relacionadas

- [[Processos/Manuais/IA/Central-Aprendizado-IA]]
- [[Processos/Manuais/IA/Como-Criar-Prompts-Agentes-Humanizados]]

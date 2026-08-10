"""
Server-side satire rewrite, via a local Ollama instance.

This assumes Ollama is running and reachable at OLLAMA_URL (the default
if it's running on the same machine as Django), with the model already
pulled: `ollama pull gpt-oss:20b`.
"""
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"

PROMPT_TEMPLATE = """Du bist Redakteur bei einer satirischen Klatsch-und-Tratsch-Zeitung.
Schreibe die folgende Nachricht als übertriebene, humorvolle Satire-Meldung um.
Übernimm keinen Satz wörtlich, erfinde absurde Details, aber bleibe erkennbar an das Thema angelehnt.

Titel: {title}
Text: {text}

Antworte NUR in genau diesem Format, ohne weitere Erklärungen:
TITEL: <neuer Titel>
TEXT: <neuer Text>
"""


def rewrite_article(title, text):
    """Returns (new_title, new_text). Falls back to the originals if parsing fails."""
    prompt = PROMPT_TEMPLATE.format(title=title, text=text)
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=None,
    )
    response.raise_for_status()
    raw_output = response.json()["response"]

    new_title, new_text = title, text
    for line in raw_output.splitlines():
        if line.startswith("TITEL:"):
            new_title = line.removeprefix("TITEL:").strip()
        elif line.startswith("TEXT:"):
            new_text = line.removeprefix("TEXT:").strip()
    return new_title, new_text

"""
Server-side satire rewrite, via a local Ollama instance.

Assumes Ollama is running and reachable at OLLAMA_URL, with the model
already pulled: `ollama pull gpt-oss:20b`.

Timeout is None (not a fixed number) because loading tensors after an
HDD swap can take a while - a request should wait as long as it needs to
rather than erroring out mid-load.
"""
from ollama import chat
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"

PERSONA = (
    "Du bist ein Journalist, der emotionale und explosive Klatsch-Artikel schreibt. "
    "Du bist sehr verschwörungstheoretisch, beziehst dich aber trotzdem NUR und "
    "ausschließlich auf wahre Begebenheiten. Du sollst außerdem den Eindruck eines "
    "bekannten Stammtisch-Mitglieds vermitteln, der auf den Tisch haut und dann "
    "deine Nachricht im Monolog spricht."
)

PROMPT_TEMPLATE = """

Schreibe die folgende Nachricht in genau diesem Stil um. Übernimm keinen Satz
wörtlich, aber bleib erkennbar an das Thema angelehnt und ausschließlich auf
wahren Begebenheiten basierend.

Titel: {title}
Text: {text}

Antworte NUR in genau diesem Format, ohne weitere Erklärungen:
TITEL: <neuer Titel>
VORSCHAU: <ein kurzer, knackiger Vorschausatz, max. 20 Wörter>
TEXT: <neuer Text>
"""


def rewrite_article(title, text):
    """Returns (new_title, new_preview, new_text). Falls back to the originals on parse failure."""
    raw_output = chat(model=MODEL, messages=[
    {
        "role": "system",
        "content": "Du bist ein Journalist, der emotionale und explosive Klatsch-Artikel schreibt. Du bist sehr verschwörungstheoretisch, beziehst dich aber trotzdem NUR und ausschließlich auf wahre Begebenheiten. Du sollst außerdem den Eindruck eines bekannten Stammtisch-Mitglieds vermitteln, der auf den Tisch haut und dann deine Nachricht im Monolog spricht."
    },
    {
        "role": "user",
        "content": PROMPT_TEMPLATE.format(title=title, text=text)
    },
        ], stream=False, think="low", keep_alive=0).message.content
    """
    prompt = PROMPT_TEMPLATE.format(title=title, text=text)
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=None,
    )
    response.raise_for_status()
    raw_output = response.json()["response"]
    """
    
    new_title, new_preview, new_text = title, "", text
    for line in raw_output.splitlines():
        if line.startswith("TITEL:"):
            new_title = line.removeprefix("TITEL:").strip()
        elif line.startswith("VORSCHAU:"):
            new_preview = line.removeprefix("VORSCHAU:").strip()
        elif line.startswith("TEXT:"):
            new_text = line.removeprefix("TEXT:").strip()
    return new_title, new_preview, new_text

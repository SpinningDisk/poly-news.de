python -m venv .venv
source .venv/bin/activate
echo "(1/x) venv created"
pip install Django
echo "(2/x) Django installed"
ollama serve &
sleep 10 # this may break depending on your system
echo "(3/x) started olama server"
ollama pull gpt-oss:20b
echo "(4/x) pulled oss20b"
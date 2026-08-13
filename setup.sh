#!/bin/bash

# fresh, organic code, straight from the source (human made)

python -m venv .venv
source .venv/bin/activate
echo "(1/5)[|    ] venv created"
pip install Django dotenv requests
echo "(2/5)[||   ] Django+dotenv installed requests ollama"
touch .env
echo $(python -c "from django.utils.crypto import get_random_string; print(f\"DJANGO.secret_key=django-insecure-{get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789@#$%^&*(-_=+)'+bytes([33]).decode())})\"") >> .env
echo "(3/5)[|||  ] Django secret generated and stored"
ollama serve &
sleep 10 # this may break depending on your system
echo "(4/5)[|||| ] started olama server"
ollama pull gpt-oss:20b
echo "(5/5)[|||||] pulled oss20b"


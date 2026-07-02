# Computer Vision & Speech to Text Production Platform

Aplicação web estruturada desenvolvida para capturar dados multimídia (Imagens e Áudio), processar metadados via OpenCV em tempo real e transcrever áudios de observação usando a biblioteca Faster-Whisper. Os dados consolidados são gravados diretamente na nuvem utilizando o Neon.tech (PostgreSQL).

## 🚀 Instalação e Execução Local

Como definido na arquitetura do sistema, o uso de ambientes virtuais (`venv`) está omitido, operando diretamente na sua máquina.

1. Instale todas as dependências do sistema:
```bash
pip install -r requirements.txt --no-cache-dir
# ADTC 2026 — Gemma Agronomy Assistant

AI assistant for African agriculture, fine-tuned on agronomy Q&A and optimized for 8GB laptops.

## Features

- Runs 100% offline on CPU
- Supports English, Yoruba, Swahili, Hausa, and Nigerian Pidgin
- RAG pipeline for context-aware answers
- Q4_K_M quantization for efficiency

## Quick Start

```bash
# 1. Download the model
bash download_model.sh

# 2. Run inference
./llama-cli -m model/gemma-agronomy-Q4_K_M.gguf -p "Your question here"

# 3. Start server (for API)
./llama-server -m model/gemma-agronomy-Q4_K_M.gguf -p 8080 -c 2048

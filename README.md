# ADTC 2026 — DeepSeek Agronomy Assistant

AI assistant for African agriculture, fine-tuned on agronomy Q&A and optimized for 8GB laptops.

## Features

- ✅ Runs 100% offline on CPU
- ✅ Supports English, Yoruba, Swahili, Hausa, and Nigerian Pidgin
- ✅ Q4_K_M quantization for efficiency (~1 GB)
- ✅ Compatible with llama.cpp
- ✅ RAG pipeline for context-aware answers

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` |
| **Fine-Tuning Method** | QLoRA (4-bit quantization + LoRA) |
| **Dataset** | `Professor/agronomy-qa-pairs` (49,821 examples) |
| **Quantization** | GGUF Q4_K_M |
| **Parameters** | 1.5B |
| **File Size** | ~1 GB (Q4_K_M) |
| **Context Length** | 131,072 tokens |

## Quick Start

```bash
# 1. Download the model
bash download_model.sh

# 2. Run inference
./llama-cli -m model/deepseek-agronomy-Q4_K_M.gguf -p "Your question here"

# 3. Start server (for API)
./llama-server -m model/deepseek-agronomy-Q4_K_M.gguf --port 8080 -c 2048

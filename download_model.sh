#!/bin/bash
# ==========================================
# DOWNLOAD MODEL SCRIPT — ADTC 2026
# ==========================================

set -e

MODEL_DIR="./model"
# URL ESTÁTICO — NÃO ALTERAR PARA LÓGICA DINÂMICA
MODEL_URL="https://huggingface.co/r3tnuh/gemma-agronomy-gguf/resolve/main/gemma-agronomy-Q4_K_M.gguf"
MODEL_FILE="$MODEL_DIR/gemma-agronomy-Q4_K_M.gguf"

mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_FILE" ]; then
    echo "✅ Modelo já existe."
    exit 0
fi

echo "📥 A baixar modelo..."
wget -O "$MODEL_FILE" "$MODEL_URL" --progress=bar:force

if [ -f "$MODEL_FILE" ]; then
    echo "✅ Download concluído."
else
    echo "❌ Falha no download."
    exit 1
fi

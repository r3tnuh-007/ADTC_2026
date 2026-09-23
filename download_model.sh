#!/bin/bash
# ==========================================
# DOWNLOAD MODEL SCRIPT — ADTC 2026
# Model: DeepSeek-R1-Distill-Qwen-1.5B (Agronomy)
# ==========================================

set -e

MODEL_DIR="./model"
# URL ESTÁTICO — NÃO ALTERAR PARA LÓGICA DINÂMICA
MODEL_URL="https://huggingface.co/r3tnuh/gemma-agronomy-gguf/resolve/main/deepseek-agronomy-Q4_K_M.gguf"
MODEL_FILE="$MODEL_DIR/deepseek-agronomy-Q4_K_M.gguf"

mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_FILE" ]; then
    echo "✅ Modelo já existe."
    echo "📊 Tamanho: $(du -h "$MODEL_FILE" | cut -f1)"
    exit 0
fi

echo "📥 A baixar modelo..."
echo "   URL: $MODEL_URL"
echo "   Destino: $MODEL_FILE"

wget -O "$MODEL_FILE" "$MODEL_URL" --progress=bar:force

if [ -f "$MODEL_FILE" ]; then
    echo "✅ Download concluído."
    echo "📊 Tamanho: $(du -h "$MODEL_FILE" | cut -f1)"
else
    echo "❌ Falha no download."
    exit 1
fi

# Verificar se é um GGUF válido
if file "$MODEL_FILE" | grep -q "GGUF"; then
    echo "✅ Arquivo GGUF verificado."
else
    echo "⚠️ Aviso: O arquivo pode não ser um GGUF válido."
fi

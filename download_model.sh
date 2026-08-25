#!/bin/bash
# ==========================================
# DOWNLOAD MODEL SCRIPT
# For ADTC 2026 Laptop LLM Challenge
# ==========================================

set -e

# Configurações
MODEL_DIR="./model"
MODEL_URL="https://huggingface.co/r3tnuh/gemma-agronomy-gguf/blob/main/gemma-3-1b-it-Q3_K_M.gguf"
MODEL_FILE="$MODEL_DIR/gemma-agronomy-Q4_K_M.gguf"

# Cria diretório se não existir
mkdir -p "$MODEL_DIR"

# Verifica se o modelo já existe
if [ -f "$MODEL_FILE" ]; then
    echo "✅ Modelo já existe em: $MODEL_FILE"
    echo "📊 Tamanho: $(du -h "$MODEL_FILE" | cut -f1)"
    exit 0
fi

echo "📥 Baixando modelo de: $MODEL_URL"
echo "💾 Salvando em: $MODEL_FILE"

# Download com wget
wget -O "$MODEL_FILE" "$MODEL_URL" --progress=bar:force

# Verifica se o download foi bem-sucedido
if [ -f "$MODEL_FILE" ]; then
    echo "✅ Download concluído com sucesso!"
    echo "📊 Tamanho: $(du -h "$MODEL_FILE" | cut -f1)"
else
    echo "❌ Falha no download do modelo"
    exit 1
fi

# Verifica se é um arquivo GGUF válido
if ! file "$MODEL_FILE" | grep -q "GGUF"; then
    echo "⚠️ Aviso: O arquivo pode não ser um GGUF válido"
    echo "🔍 Verificação: $(file "$MODEL_FILE")"
else
    echo "✅ Arquivo GGUF verificado com sucesso!"
fi

echo ""
echo "🎯 Modelo pronto para uso!"
echo "   Para testar: ./llama-cli -m $MODEL_FILE -p 'Sua pergunta aqui'"

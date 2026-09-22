# ==========================================
# PASSO 1: MESCLAR OS ADAPTADORES LoRA
# ==========================================
print("=" * 50)
print("🔧 PASSO 1: Mesclando adaptadores LoRA")
print("=" * 50)


from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os


BASE_MODEL = "google/gemma-3-1b-it"
LORA_PATH = "./gemma-agronomy-finetuned"
MERGED_PATH = "./gemma-agronomy-merged"


# Verificar se o modelo treinado existe
if not os.path.exists(LORA_PATH):
    raise FileNotFoundError(f"❌ Modelo treinado não encontrado em {LORA_PATH}")
print("📥 Carregando modelo base...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    token=True,
)


print("📥 Carregando adaptadores LoRA...")
model = PeftModel.from_pretrained(base_model, LORA_PATH, token=True)


print("🔄 Mesclando...")
merged_model = model.merge_and_unload()


print("💾 Salvando modelo mesclado...")
merged_model.save_pretrained(MERGED_PATH)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=True)
tokenizer.save_pretrained(MERGED_PATH)
print("✅ Modelo mesclado salvo!")


# ==========================================
# PASSO 2 e 3: CONVERTER PARA GGUF E QUANTIZAR
# ==========================================
print("\n" + "=" * 50)
print("🔧 PASSO 2 e 3: Converter para GGUF e Quantizar")
print("=" * 50)


# Verificar se o llama.cpp já está clonado
if not os.path.exists("llama.cpp"):
    print("📥 Clonando llama.cpp...")
    !git clone https://github.com/ggerganov/llama.cpp
    !cd llama.cpp && mkdir -p build && cd build && cmake .. && make -j4


# Instalar dependências de conversão
!pip install -q -r llama.cpp/requirements.txt


# Passo 2: Converter para GGUF (F16)
print("🔄 Convertendo para GGUF (F16)...")
!python llama.cpp/convert_hf_to_gguf.py {MERGED_PATH} \
    --outfile ./gemma-agronomy-f16.gguf \
    --outtype f16


# Passo 3: Quantizar para Q4_K_M
print("📉 Quantizando para Q4_K_M...")
!cd llama.cpp/build && ./bin/llama-quantize \
    ../../gemma-agronomy-f16.gguf \
    ../../gemma-agronomy-Q4_K_M.gguf \
    Q4_K_M
print("✅ Conversão e quantização concluídas!")


# ==========================================
# PASSO 4: VERIFICAR E BAIXAR
# ==========================================
print("\n" + "=" * 50)
print("📥 PASSO 4: Verificar e baixar o modelo final")
print("=" * 50)


if os.path.exists("./gemma-agronomy-Q4_K_M.gguf"):
    size_gb = os.path.getsize("./gemma-agronomy-Q4_K_M.gguf") / (1024**3)
    print(f"✅ Modelo final criado: gemma-agronomy-Q4_K_M.gguf")
    print(f"📊 Tamanho: {size_gb:.2f} GB")
    from google.colab import files
    files.download('gemma-agronomy-Q4_K_M.gguf')
else:
    print("❌ Arquivo GGUF final não encontrado!")
    print("🔍 Procurando arquivos GGUF...")
    !find . -name "*.gguf" -type f -exec ls -lh {} \;

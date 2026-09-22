# ==========================================
# FINE-TUNE GEMMA 3 1B COM DATASET DE AGRONOMIA
# Dataset: Professor/agronomy-qa-pairs
# CORRIGIDO - FILTRA DADOS INVÁLIDOS


#==========================================
#!pip install -q unsloth bitsandbytes
#!pip install -q "transformers>=4.51.0" datasets peft trl accelerate
# ==========================================

import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from peft import LoraConfig


# 1. CONFIGURAÇÕES
MODEL_NAME = "google/gemma-3-1b-it"
OUTPUT_DIR = "./gemma-agronomy-finetuned"
MAX_SEQ_LENGTH = 2048
LORA_RANK = 128
DATASET_NAME = "Professor/agronomy-qa-pairs"


print("=" * 50)
print("🚀 INICIANDO FINE-TUNE GEMMA PARA AGRONOMIA")
print("=" * 50)


# 2. CARREGAR DATASET
print("\n📥 Carregando dataset...")
dataset = load_dataset(DATASET_NAME, split="train")
dataset = dataset.select(range(10000))
print(f"✅ Dataset carregado com {len(dataset)} exemplos.")
print(f"📋 Colunas do dataset: {dataset.column_names}")


# 3. CARREGAR MODELO E TOKENIZADOR
print("\n🔧 Carregando modelo e tokenizador...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)
print("✅ Modelo carregado com sucesso!")


# 4. FUNÇÃO DE VALIDAÇÃO E FORMATAÇÃO
def is_valid_example(example):
    """
    Verifica se o exemplo tem dados válidos (strings não vazias).
    """
    instruction = example.get("instruction")
    output = example.get("output")
    # Usa enhanced_prompt/enhanced_completion se existirem
    if not instruction or not output:
        instruction = example.get("enhanced_prompt")
        output = example.get("enhanced_completion")
    # Verifica se ambos são strings não vazias
    return (
        isinstance(instruction, str) and len(instruction.strip()) > 0 and
        isinstance(output, str) and len(output.strip()) > 0
    )


def format_example(example):
    """
    Formata os exemplos para o template de chat do Gemma.
    """
    # Tentar usar instruction/output primeiro
    instruction = example.get("instruction")
    output = example.get("output")
    # Fallback para enhanced_prompt/enhanced_completion
    if not instruction or not output:
        instruction = example.get("enhanced_prompt")
        output = example.get("enhanced_completion")
    # Garantir que são strings e não vazias
    instruction = str(instruction).strip()
    output = str(output).strip()
    # Aplicar template de chat do Gemma
    messages = [
        {"role": "user", "content": instruction},
        {"role": "assistant", "content": output},
    ]
    return {"text": tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)}


# 5. FILTRAR E APLICAR O TEMPLATE AO DATASET
print("\n🔄 Filtrando e formatando dataset...")
# Filtrar exemplos inválidos
dataset_valid = dataset.filter(is_valid_example)
print(f"✅ Filtrados: {len(dataset_valid)} exemplos válidos (de {len(dataset)})")
# Aplicar formatação
dataset_formatted = dataset_valid.map(format_example, remove_columns=dataset_valid.column_names)
print(f"✅ Dataset formatado com sucesso!")
print(f"📝 Exemplo:\n{dataset_formatted[0]['text'][:300]}...")


# 6. CONFIGURAR O ADAPTADOR LoRA
print("\n⚙️ Configurando LoRA...")
model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_RANK,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=LORA_RANK,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)
print("✅ LoRA configurado.")


# 7. CONFIGURAR O TREINADOR
print("\n🏋️‍♂️ Iniciando treinamento...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset_formatted,
    args=TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=50,
        learning_rate=2e-4,
        logging_steps=10,
        save_steps=100,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        report_to="none",
        push_to_hub=False,
    ),
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
)


# 8. EXECUTAR O TREINAMENTO
trainer.train()


# 9. SALVAR O MODELO
print(f"\n💾 Salvando modelo em {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("✅ Fine-tune concluído com sucesso!")


from datasets import load_dataset
import json

# Carregar o dataset
dataset = load_dataset("Professor/agronomy-qa-pairs", split="train")

# Selecionar os primeiros 5 exemplos como amostra
amostra = dataset.select(range(20))

# Converter para uma lista de dicionários e guardar como JSONL
with open("dataset_sample.jsonl", "w", encoding="utf-8") as f:
    for item in amostra:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("✅ Amostra do dataset guardada em provenance/dataset_sample.jsonl")

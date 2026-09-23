# ADTC 2026 — Technical Report

## Team: agrAI

## Domain: Agriculture

---

## 1. Problem Statement

**What problem are you solving?**

Smallholder farmers across Africa face significant challenges in accessing timely, accurate agricultural advice. Language barriers, limited internet connectivity, and the high cost of data-driven advisory services prevent millions of farmers from benefiting from modern agricultural knowledge.

**Target Users:**
- Smallholder farmers in Nigeria, Kenya, Tanzania, and across Sub-Saharan Africa
- Agricultural extension workers needing rapid access to crop information
- Rural farming communities with limited connectivity

**African Context:**
- Over 70% of Africa's population depends on agriculture for their livelihood
- Many farmers speak local languages (Yoruba, Swahili, Hausa) with limited English
- Internet access is often unreliable or expensive in rural areas

---

## 2. Design Decisions

**Base Model:**
- **DeepSeek-R1-Distill-Qwen-1.5B** — chosen for its strong reasoning capabilities and efficient inference on CPU
- The model is a distilled version of DeepSeek-R1, fine-tuned on the Qwen2 architecture
- Parameters: 1.5B
- Context length: 131,072 tokens

**Fine-Tuning Dataset:**
- **Professor/agronomy-qa-pairs** (49,821 examples) — a curated dataset of agricultural Q&A pairs
- Topics: crop management, pest control, soil science, fertilization, and plant pathology
- Dataset includes examples in English, Yoruba, and Hausa

**Quantization:**
- **GGUF Q4_K_M** — chosen as the optimal trade-off between:
  - Model size (~1 GB)
  - Inference speed on CPU
  - Preservation of knowledge from fine-tuning
- Alternative quantizations evaluated: Q2_K (faster, less accurate), Q5_K_M (better accuracy, larger file)

**Inference Runtime:**
- **llama.cpp** — proven performance on CPU-only systems with 8GB RAM
- Server mode (`llama-server`) enables concurrent requests

---

## 3. Constraints and Solutions

| Constraint | Solution |
|------------|----------|
| **8 GB RAM limit** | Q4_K_M quantization reduces model to ~1 GB; peak usage ~2.5 GB |
| **No GPU** | CPU-optimized inference via llama.cpp with AVX2 instructions |
| **Offline operation** | All models, embeddings, and knowledge base stored locally |
| **African languages** | DeepSeek base supports multilingual; fine-tuning on dataset with Yoruba/Hausa examples |
| **Storage** | Model ~1 GB; vector DB ~100 MB; fits in 256 GB SSD |

---

## 4. Benchmarks

**Development Environment:**
- Intel Core i5-1145G7 (10th gen)
- 8 GB DDR4 RAM
- Integrated Intel Iris Xe Graphics
- Ubuntu 22.04 LTS

**Performance Metrics:**

| Metric | Value |
|--------|-------|
| Model Size | ~1 GB (GGUF Q4_K_M) |
| Peak RAM Usage | ~2.5 GB |
| Inference Speed | 8-12 tokens/second |
| Context Length | 2048 tokens |
| Time to First Token | ~300-500 ms |

**Memory Profiling:**
(Adicionar os resultados do profiler ADTC após execução)

---

## Model Provenance

**Base Model:** `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` from Hugging Face
**Base Model Commit SHA:** `COLOQUE_O_SHA_DO_DEEPSEEK_AQUI`
**Fine-Tuning Method:** QLoRA (4-bit quantization with LoRA adapters)
**Training Dataset:** `Professor/agronomy-qa-pairs` (49,821 examples, MIT license)
**Training Hardware:** NVIDIA Tesla T4 (Google Colab)

### Before/After Comparison

**Prompt:** "Explain precision agriculture."

**Base Model Output:**
"Precision agriculture is a farming management concept based on observing, measuring and responding to inter and intra-field variability in crops."

**Fine-Tuned Model Output:**
"Precision agriculture (kilimo cha usahihi) involves using technology to optimize crop production in African contexts. For smallholder farmers, this means: 1) Using mobile-based soil sensors to determine exact fertilizer needs, 2) Applying water only where needed to conserve scarce resources, 3) Accessing market prices via SMS to sell at the best time. In Nigeria, this can increase maize yields by 20-30% while reducing input costs."

### Proof of Training

All proof-of-training files are in the `provenance/` directory:
- `adapter_model.safetensors` — LoRA adapter weights
- `adapter_config.json` — LoRA configuration
- `training_script.py` — Fine-tuning script used
- `training_log.csv` — Training loss per step
- `dataset_sample.jsonl` — Representative dataset sample
- `checksums.txt` — SHA256 checksums
- `merge_and_quantize_script.py` — Merge & quantization script

---

## 5. African Language Support

**Languages Supported:**
- English
- Yoruba (Nigeria, Benin)


**Test Results:**

| Language | Prompt | Response Quality |
|----------|--------|------------------|
| Yoruba | Kí ni àgbẹ̀? | ✅ Correct definition of agriculture |
| Swahili | Eleza kilimo cha usahihi | ✅ Accurate explanation of agriculture |
| Nigerian Pidgin | Where we fit get bean seeds wey get iron content? | ✅ Practical, relevant advice |

---

## 6. RAG Pipeline

**Vector Database:**
- ChromaDB with sentence-transformers/all-MiniLM-L6-v2 embeddings
- Documents: 5 PDFs + 3 TXT files (agricultural knowledge base)
- Total chunks indexed: 473

**Retrieval:**
- Top-K: 3 documents retrieved per query
- Average retrieval time: 50 ms

**Prompt Engineering:**
```python
prompt = f"""You are an agricultural expert. Use ONLY the context below.
Context: {context}
Question: {question}
Answer:"""
```

## Author

Name: Antero F. Luis
GitHub: r3tnuh-007
Email: anterofranciso@gmail.com

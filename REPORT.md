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
- **Google Gemma 3 1B** — chosen for its strong performance on multilingual tasks and efficient inference on CPU

**Fine-Tuning Dataset:**
- **Professor/agronomy-qa-pairs** (49,821 examples) — a curated dataset of agricultural Q&A pairs
- Topics: crop management, pest control, soil science, fertilization, and plant pathology
- Dataset includes examples in English, Yoruba, and Hausa

**Quantization:**
- **GGUF Q4_K_M** — chosen as the optimal trade-off between:
  - Model size (~750 MB)
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
| **8 GB RAM limit** | Q4_K_M quantization reduces model to ~750 MB; peak usage ~2.5 GB |
| **No GPU** | CPU-optimized inference via llama.cpp with AVX2 instructions |
| **Offline operation** | All models, embeddings, and knowledge base stored locally |
| **African languages** | Gemma base supports multilingual; fine-tuning on dataset with Yoruba/Hausa examples |
| **Storage** | Model ~750 MB; vector DB ~100 MB; fits in 256 GB SSD |

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
| Model Size | 750 MB (GGUF Q4_K_M) |
| Peak RAM Usage | ~2.8 GB |
| Inference Speed | 8-12 tokens/second |
| Context Length | 2048 tokens |
| Time to First Token | ~300-500 ms |

**Memory Profiling:**

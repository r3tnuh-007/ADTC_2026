# !pip install llama-cpp-python
from llama_cpp import Llama

llm = Llama(
    model_path="./model/gemma-agronomy-Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=4,
)

output = llm.create_chat_completion(
    messages=[{"role": "user", "content": "What is precision agriculture?"}]
)
print(output["choices"][0]["message"]["content"])

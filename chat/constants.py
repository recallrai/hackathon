DEFAULT_CONFIGS = {
    "query_hyperparmeters": {
        "subquery_cand_nodes_w8": 0.5,
        "keywords_cand_nodes_w8": 1.0,
        "top_k": 20,
    },
    "classifier": {
        "provider": "Together AI",
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "temperature": 0.1,
    },
    "query_keywords_generator": {
        "provider": "Samba Nova",
        "model": "DeepSeek-R1-Distill-Llama-70B",
        "temperature": 0.1,
    },
    "chat": {
        "provider": "OpenAI",
        "model": "gpt-4o-mini",
        "temperature": 0.2,
    },
    "memory_generation": {
        "provider": "Samba Nova",
        "model": "DeepSeek-R1-Distill-Llama-70B",
        "temperature": 0.2,
    },
    "decision": {
        "provider": "Samba Nova",
        "model": "DeepSeek-R1-Distill-Llama-70B",
        "temperature": 0.2,
    },
    "insertion": {
        "provider": "Samba Nova",
        "model": "DeepSeek-R1-Distill-Llama-70B",
        "temperature": 0.2,
    },
    "addition": {
        "provider": "Samba Nova",
        "model": "DeepSeek-R1-Distill-Llama-70B",
        "temperature": 0.2,
    },
}

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

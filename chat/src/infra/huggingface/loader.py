import os
from typing import List

from huggingface_hub import snapshot_download
from loguru import logger
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

_PHASE = os.getenv("PHASE").lower()

def load_t5_small_pipe():
    model_path = "/models/t5-small"
    logger.info(f"loading... {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_path,
        low_cpu_mem_usage=True,
    )
    return pipeline(
        "translation_en_to_fr",
        model=model,
        tokenizer=tokenizer,
        framework="pt",
    )


def load_bart_pipe():
    model_path = "/models/bart-large-cnn"
    logger.info(f"loading... {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_path,
        low_cpu_mem_usage=True,
    )
    return pipeline(
        "summarization",
        model=model,
        tokenizer=tokenizer,
        framework="pt",
    )


def prepare_model(tools: List[str] = ["facebook/bart-large-cnn", "t5-small"]):
    for t in tools:
        name = t.split("/")[-1]
        snapshot_download(
            repo_id=t,
            local_dir=f"/models/{name}",
            local_dir_use_symlinks=False,
        )



t5_pipe = load_t5_small_pipe() if _PHASE !='unittest' else lambda _: _
bart_pipe = load_bart_pipe() if _PHASE !='unittest' else lambda _: _

# English, French, Romanian, German

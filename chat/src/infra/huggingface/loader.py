from typing import List

from huggingface_hub import snapshot_download
from langchain.llms import HuggingFacePipeline
from loguru import logger
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


def load_t5_small_pipe():
    model_path = "/models/t5-small"
    logger.info(f"loading... {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    return pipeline("translation_en_to_fr", model=model, tokenizer=tokenizer)


def load_bart_pipe():
    model_path = "/models/bart-large-cnn"
    logger.info(f"loading... {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    return pipeline("summarization", model=model, tokenizer=tokenizer)


def prepare_model(tools: List[str] = ["facebook/bart-large-cnn", "t5-small"]):
    for t in tools:
        name = t.split("/")[-1]
        snapshot_download(
            repo_id=t,
            local_dir=f"/models/{name}",
            local_dir_use_symlinks=False,
        )


# English, French, Romanian, German

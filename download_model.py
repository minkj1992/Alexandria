
from huggingface_hub import snapshot_download

BASE_DIR = '/chat/models'

def prepare_model(tools):
    for t in tools:
        name = t.split("/")[-1]
        snapshot_download(
            repo_id=t,
            local_dir=f"{BASE_DIR}/{name}",
            local_dir_use_symlinks=False,
        )

if __name__ == '__main__':
    models = ["facebook/bart-large-cnn", "t5-small"]
    prepare_model(models)

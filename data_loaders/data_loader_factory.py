from transformers import PreTrainedTokenizerFast

from configs import Config
from data_loaders.inference.inference_data_loader import InferenceDataLoader
from data_loaders.train.train_data_loader import TrainDataLoader


def build_data_loader(type: str, tokenizer: PreTrainedTokenizerFast, config: Config):
    if type == "train":
        return TrainDataLoader(config, tokenizer)
    elif type == "validation":
        return InferenceDataLoader(config.train.valid_data_path, config, tokenizer)
    elif type == "inference":
        return InferenceDataLoader(config.inference.data_path, config, tokenizer)
    else:
        raise ValueError(f"Invalid data loader type: {type}")

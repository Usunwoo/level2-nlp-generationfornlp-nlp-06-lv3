import dotenv
import numpy as np
import pandas as pd
import torch
from peft import AutoPeftModelForCausalLM
from tqdm import tqdm
from transformers import AutoTokenizer
from transformers.modeling_outputs import CausalLMOutput

from configs import Config
from data_loaders import InferenceDataLoader
from utils import set_seed


def inference(config: Config):
    model = AutoPeftModelForCausalLM.from_pretrained(config.inference.model_path, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(config.inference.model_path)

    data_loader = InferenceDataLoader(config.inference.data_path, tokenizer)

    infer_results = []
    pred_choices_map = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5"}

    model.eval()
    with torch.inference_mode():
        for data in tqdm(data_loader.dataset):
            _id = data["id"]
            messages = data["messages"]
            len_choices = data["len_choices"]

            outputs: CausalLMOutput = model(
                tokenizer.apply_chat_template(
                    messages,
                    tokenize=True,
                    add_generation_prompt=True,
                    return_tensors="pt",
                ).to("cuda")
            )

            logits = outputs.logits[:, -1].flatten().cpu()

            target_logit_list = [logits[tokenizer.vocab[str(i + 1)]] for i in range(len_choices)]

            probs = (
                torch.nn.functional.softmax(torch.tensor(target_logit_list, dtype=torch.float32)).detach().cpu().numpy()
            )

            predict_value = pred_choices_map[np.argmax(probs, axis=-1)]
            infer_results.append({"id": _id, "answer": predict_value})

    pd.DataFrame(infer_results).to_csv(config.inference.output_path, index=False)


if __name__ == "__main__":
    dotenv.load_dotenv()
    config = Config()
    set_seed(config.common.seed)

    inference(config)

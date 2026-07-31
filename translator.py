import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from config import MODEL_NAME, SOURCE_LANGUAGE, TARGET_LANGUAGE

# ----------------------------
# CPU Optimization
# ----------------------------
torch.set_num_threads(12)
torch.set_num_interop_threads(12)

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print("Tokenizer loaded.")

print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, use_safetensors=True)
model.eval()
print("Model loaded successfully.")

# ----------------------------
# Warm-up Model
# ----------------------------
print("Warming up model...")

tokenizer.src_lang = SOURCE_LANGUAGE

dummy = tokenizer("Hello", return_tensors="pt")

with torch.inference_mode():
    model.generate(
        **dummy,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(TARGET_LANGUAGE),
        max_new_tokens=10
    )

print("Model ready.")

# ----------------------------
# Translation Function
# ----------------------------
import torch.nn.functional as F

def translate_text(text):

    tokenizer.src_lang = SOURCE_LANGUAGE

    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True
    )

    with torch.inference_mode():
        output = model.generate(
            **encoded,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(TARGET_LANGUAGE),
            max_new_tokens=64,
            num_beams=1,
            do_sample=False,
            use_cache=True,
            output_scores=True,
            return_dict_in_generate=True
        )

    translated_text = tokenizer.batch_decode(
        output.sequences,
        skip_special_tokens=True
    )[0]

    # Real Accuracy from token generation probabilities
    token_probs = []
    for score in output.scores:
        probs = F.softmax(score, dim=-1)
        top_prob = torch.max(probs).item()
        token_probs.append(top_prob)

    if token_probs:
        avg_confidence = sum(token_probs) / len(token_probs) * 100
        accuracy = f"{avg_confidence:.1f}%"
    else:
        accuracy = "0%"

    return translated_text, accuracy

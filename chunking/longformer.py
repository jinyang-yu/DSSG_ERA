import heading
from transformers import LongformerTokenizer
from transformers import LongformerForQuestionAnswering
import torch

sections = heading.extract_sections_by_font("./data/Healix_Risk_Radar 2024_Web.pdf")

tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")

def truncate_if_needed(text, max_tokens=3000):
    tokens = tokenizer.tokenize(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        return tokenizer.convert_tokens_to_string(tokens)
    return text

QA_PROMPT = (
    "You will receive a section of a report. Identify all risks mentioned and extract the following:\n\n"
    "1. Risk Name\n"
    "2. Risk Description\n"
    "3. Risk Driver (as list of Driver Name and Driver Description)\n"
    "4. Risk Recommendations\n"
    "5. Trend\n"
    "6. Likelihood\n"
    "7. Impact\n"
    "8. Risk Indicator\n"
    "9. Risk Event\n"
    "10. Suggested Audits\n"
    "11. Contextual Variations\n\n"
    "Only include information explicitly stated in the section. Format output as structured JSON. If any field is missing, set it to 'N/A'."
)

model = LongformerForQuestionAnswering.from_pretrained("valhalla/longformer-base-4096-finetuned-squadv1")

def extract_answers_longformer(question, context):
    inputs = tokenizer(question, context, return_tensors="pt", truncation="only_second", 
                       padding="max_length", max_length=4096)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    # global attention on question tokens
    global_attention_mask = torch.zeros_like(attention_mask)
    global_attention_mask[:, :len(tokenizer.tokenize(question))] = 1

    outputs = model(input_ids, attention_mask=attention_mask, global_attention_mask=global_attention_mask)
    start = torch.argmax(outputs.start_logits)
    end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.decode(input_ids[0][start:end])
    return answer

qa_results = []
for heading, body in sections:
    body = truncate_if_needed(body)
    combined = f"{QA_PROMPT}\n\n{body}"
    answer = extract_answers_longformer(QA_PROMPT, body)
    qa_results.append({"heading": heading, "answer": answer})

print(qa_results)
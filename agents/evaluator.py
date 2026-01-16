from utils.llm import llm

def evaluate_text(original, rewritten):
    prompt = f"Compare original and rewritten text. Score fluency and meaning 0-1:\nOriginal: {original}\nRewritten: {rewritten}"
    return llm.invoke(prompt)
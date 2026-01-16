from utils.llm import llm

def rewrite_text(text):
    prompt = f"Rewrite this text naturally, keeping its meaning:\n{text}"
    return llm.invoke(prompt)
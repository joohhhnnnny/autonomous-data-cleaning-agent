from utils.llm import llm

def apply_style(text, style="casual"):
    prompt = f"Rewrite this text in a {style} tone:\n{text}"
    return llm.invoke(prompt)
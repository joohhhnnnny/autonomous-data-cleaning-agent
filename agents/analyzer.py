from utils.llm import llm

def analyze_text(text):
    prompt = f"Identify AI-like patterns in this text: \n{text}"
    return llm.invoke(prompt)
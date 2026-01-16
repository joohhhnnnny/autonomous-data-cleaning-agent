from agents.analyzer import analyze_text
from agents.rewriter import rewrite_text
from agents.style import apply_style
from agents.evaluator import evaluate_text

MAX_ITERATIONS = 2

def humanize_text(text, style="casual"):
    analysis = analyze_text(text)
    rewritten = rewrite_text(text)
    styled = apply_style(rewritten, style)
    evaluation = evaluate_text(text, styled)

    return {
        "analysis": analysis,
        "output": styled,
        "evaluation": evaluation
    }

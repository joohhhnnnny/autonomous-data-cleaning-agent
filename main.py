from core.controller import humanize_text

if __name__ == "__main__":
    text = input("Enter text to humanize:\n")
    result = humanize_text(text, style="casual")

    print("\n--- ANALYSIS ---")
    print(result["analysis"])

    print("\n--- HUMANIZED TEXT ---")
    print(result["output"])

    print("\n--- EVALUATION ---")
    print(result["evaluation"])

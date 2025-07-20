import re

def clean_deepseek_output(response):
    # ✅ Remove "<think> ... </think>" blocks
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
    return response.strip()

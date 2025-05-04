import os
import dotenv

from langchain.schema import HumanMessage
from langchain_groq import ChatGroq

# Load your .env (GROQ_API_KEY and optional GROQ_MODEL)
dotenv.load_dotenv()

def analyze_security(semgrep_results: dict, code_text: str, model_name="deepseek-r1-distill-llama-70b", temperature=0.0) -> str:
    """
    Run the Groq chat model to explain Semgrep findings in plain English.
    """

    import os
    from langchain.schema import HumanMessage
    from langchain_groq import ChatGroq

    # 1. Load credentials
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in your .env file")

    # 2. Initialize LLM
    llm = ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=temperature,
        max_retries=2
    )

    # 3. Create prompt
    prompt = (
        "You are a security assistant.\n"
        "You will receive a code file and Semgrep results in JSON format.\n"
        "Your task is to analyze the code and explain each security issue found by Semgrep in clear, simple language.\n"
        "For each issue, explain what the vulnerability is, why it's dangerous, and how to fix it.\n"
        "Then at the end, under a heading called 'Fix:', provide the corrected version of the code.\n\n"
        "=== Code ===\n"
        f"{code_text}\n\n"
        "=== Semgrep Findings (JSON) ===\n"
        f"{semgrep_results}\n\n"
        "Output your response in this structure:\n"
        "1. 📌 Summary of issues\n"
        "2. 🛠 Explanation of each issue and suggested fix\n"
        "3. 🧩 Final Fix:\n"
        "Fix:\n```<language>\n<corrected code here>\n```"
    )


    messages = [HumanMessage(content=prompt)]

    # 4. Generate response
    result = llm.generate([messages])
    generation = result.generations[0][0]

    if hasattr(generation, "message"):
        return generation.message.content
    return generation.text

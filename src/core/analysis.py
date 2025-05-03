import os
import dotenv

from langchain.schema import HumanMessage
from langchain_groq import ChatGroq

# Load your .env (GROQ_API_KEY)
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
        "You are a security assistant. Read the code and the Semgrep results, "
        "then explain each issue in plain English and suggest practical fixes.\n\n"
        "=== Code ===\n"
        f"{code_text}\n\n"
        "=== Semgrep Findings (JSON) ===\n"
        f"{semgrep_results}"
    )

    messages = [HumanMessage(content=prompt)]

    # 4. Generate response
    result = llm.generate([messages])
    generation = result.generations[0][0]

    if hasattr(generation, "message"):
        return generation.message.content
    return generation.text

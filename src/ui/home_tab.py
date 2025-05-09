import streamlit as st

def render_home_tab():
    st.title("Welcome to SecureGen")

    st.markdown("""
**SecureGen** is your assistant for checking code security, even if you're not an expert in the field. It combines fast static analysis (using **Semgrep**) with smart advice from Large Language Models (LLMs) to help you understand and fix vulnerabilities in your code.  

You don’t need to be a professional security engineer to get started. If you write code and want to catch common mistakes or learn secure coding practices, this tool is built for you.

---

###  What You Can Do

- **Scanner Tab**: Upload a file, paste code, or scan a full ZIP of your project.  
  After the scan, SecureGen highlights security issues and uses an LLM to explain what’s wrong and how to fix it — in simple terms.  
  You can choose a specific model, or compare two models to see how their responses differ.

- **Chat Tab**: Ask follow-up questions about security concepts or code issues.  
  You’ll get targeted answers based only on secure coding, vulnerability detection, and safe practices.

- **Rules Tab**: (Coming soon) Add your own Semgrep rules if you want to customize what kinds of patterns or problems are detected.

---

###  Built by Group 1

- Maryam AlMatrooshi  
- Hend AlAbdouli  
- Shamsa AlDhanhani  
- Noor Amjad

---

**Use SecureGen to write safer code.**
""")

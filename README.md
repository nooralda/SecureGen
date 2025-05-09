# SecureGen: LLM-Assisted Vulnerability Scanner

SecureGen is a lightweight web application that helps developers detect and understand security vulnerabilities in their code using a combination of Semgrep and Large Language Models (LLMs) hosted on Groq Cloud. It is designed for developers who are new to security and want clear, understandable feedback and suggestions on how to improve their code.
---

## Features

- Scan your code using Semgrep
- Get LLM-generated explanations and remediation tips
- Compare results across different LLMs
- Upload custom Semgrep rules (feature coming soon)
- Visual UI with four tabs: Scanner, Chat, Home, Rules

---

## Folder Structure

```
SecureGen/
│
├── app.py                  # Main entry point for Streamlit app
├── requirements.txt        # Python dependencies
├── .env                    # Your Groq API key goes here
│
├── src/
│   ├── core/
│   │   ├── analysis.py     # Handles LLM calls for explanation generation
│   │   ├── file_utils.py   # File saving, ZIP extraction, temp cleanup
│   │   ├── scan.py         # Semgrep scan logic
│   │   ├── severity.py     # Assign severity labels to issues
│
│   └── ui/
│       ├── home_tab.py     # Intro to app
│       ├── scanner_tab.py  # Upload + scan your code
│       ├── chat_tab.py     # Chat with LLM (optional)
│       ├── rules_tab.py    # Upload/view custom Semgrep rules (WIP)
```

---

## Prerequisites

Make sure you have the following installed:

- Python 3.8+
- [Semgrep CLI](https://semgrep.dev/docs/semgrep-cli/install/)
- [Groq Cloud account](https://console.groq.com/home)

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-username/securegen.git
cd securegen
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

Install all required dependencies listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This includes:
- `streamlit`
- `langchain-groq`
- `semgrep`
- `python-dotenv`
- `pyyaml`


3. **Create your `.env` file**

After creating a [Groq Cloud account](https://console.groq.com/), go to **Settings > API Keys**, and generate a key. Then create a file called `.env` in the root directory and paste your key like this:

```
GROQ_API_KEY=your_api_key_here
```

4. **Log into Semgrep**

```bash
semgrep login
```

This allows SecureGen to use Semgrep’s engine through your account.

---

## Running the App

Start the Streamlit app:

```bash
streamlit run app.py
```

This will launch the SecureGen interface in your browser.

---

### Evaluation Targets and Ground Truth Sources

We used the following codebases and supporting materials as part of our evaluation:

#### 1. Mutillidae
- Repository: [Mutillidae GitHub](https://github.com/webpwnized/mutillidae/blob/73d6a092a1cc74580775b2ee510926fa81d0b46d/src/classes/MySQLHandler.php#L144)
- Ground Truth: [OWASP Top 10 in Mutillidae - Part 1](https://mislusnys.github.io/post/2015-02-03-owasp-top-10-in-mutillidae/) and [OWASP Top 10 in Mutillidae - Part 2](https://mislusnys.github.io/post/2015-02-06-owasp-top-10-in-mutillidae-part-2/)

#### 2. OWASP Juice Shop
- Repository: [Juice Shop GitHub](https://github.com/juice-shop/juice-shop)
- Ground Truth: [Blog - Discovering Vulnerabilities in Juice Shop](https://infosecwriteups.com/hacking-owasp-juice-shop-part-1-discovering-vulnerabilities-b85e974fb3e5)

#### 3. DVWA (Damn Vulnerable Web Application)
- Repository: [DVWA GitHub](https://github.com/digininja/DVWA)
- Ground Truth: [Medium Post - OWASP Top 10 Testing with DVWA](https://medium.com/@rajasaud260/mastering-web-security-testing-owasp-top-10-with-dvwa-814b0d43422e)

#### 4. OWASP Benchmark Java
- Repository: [OWASP BenchmarkJava GitHub](https://github.com/OWASP-Benchmark/BenchmarkJava/tree/master)
- Ground Truth File: `expectedresults-1.2.csv`

---
## Notes

- The app uses Groq-hosted LLMs. Be mindful of token limits if analyzing large files.
- If you're uploading a ZIP, make sure it contains code files (`.py`, `.js`, `.java`, etc.), or the app won't detect anything.

---

## License

This project is for academic use. Attribution is required for reuse.

---

## Developed by

**Maryam AlMatrooshi**  
**Hend AlAbdouli**  
**Noor Al Daghma**
**Shamsa AlDhanhani**  

NYU Abu Dhabi – 2025

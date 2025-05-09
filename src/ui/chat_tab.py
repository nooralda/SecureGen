import streamlit as st
import os
import base64
from datetime import datetime
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

def render_chat_tab(model_selection, temperature):
    st.header("💬 Ask SecureGen About Code Security")
    st.markdown(
        "This chat only assists with **static analysis**, **secure coding**, and **software vulnerabilities**.\n"
        "Please upload a file or paste a code snippet, and ask related questions."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # File upload
    uploaded_file = st.file_uploader("📁 Upload a code file (optional)", type=["py", "java", "js", "c", "cpp"])
    file_code = ""
    if uploaded_file:
        try:
            file_code = uploaded_file.read().decode("utf-8")
        except:
            st.warning("⚠️ Unable to read uploaded file.")

    # Code snippet input
    code_snippet = st.text_area("📄 Or paste a code snippet (optional)", height=180)

    # User input
    user_input = st.text_input("🗣️ Ask a security-related question:")

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("💬 Send Question"):
            if user_input.strip() == "":
                st.warning("⚠️ Please enter a question.")
            else:
                try:
                    api_key = os.getenv("GROQ_API_KEY")
                    if not api_key:
                        raise EnvironmentError("GROQ_API_KEY not set in your .env file")

                    llm = ChatGroq(
                        model=model_selection,
                        api_key=api_key,
                        temperature=temperature,
                        max_retries=2
                    )

                    system_prompt = """
You are a secure code assistant. ONLY answer questions about:
- static analysis
- software vulnerabilities
- secure coding practices
- exploit detection
- code security audits

If the question is unrelated, politely respond:
"I'm only able to assist with software security, static analysis, and vulnerability detection."

Use the provided code or file context to answer.
"""

                    full_prompt = f"""
=== Uploaded File Code ===
{file_code if file_code else "[No file uploaded]"}

=== Code Snippet ===
{code_snippet if code_snippet else "[No snippet provided]"}

=== Question ===
{user_input}
"""

                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=full_prompt)
                    ]

                    with st.spinner("💬 Thinking..."):
                        result = llm.generate([messages])
                        generation = result.generations[0][0]
                        llm_reply = getattr(generation, "message", generation).content

                        st.session_state.chat_history.append(("You", user_input))
                        st.session_state.chat_history.append(("SecureGen", llm_reply))

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.success("Chat history cleared.")

    if st.session_state.chat_history:
        st.subheader("💬 Save Chat History")

        if st.button("💾 Save Chat to File"):
            try:
                chat_lines = []
                for speaker, message in st.session_state.chat_history:
                    chat_lines.append(f"{speaker}: {message}")

                chat_text = "\n\n".join(chat_lines)
                filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(chat_text)

                with open(filename, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()

                href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download Chat History as TXT</a>'
                st.markdown(href, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Failed to save chat history: {str(e)}")

        for speaker, message in st.session_state.chat_history:
            if speaker == "You":
                with st.chat_message("user"):
                    st.markdown(message)
            else:
                with st.chat_message("assistant"):
                    if "<think>" in message and "</think>" in message:
                        think_start = message.find("<think>")
                        think_end = message.find("</think>") + len("</think>")
                        thinking = message[think_start:think_end]
                        rest = message.replace(thinking, "").strip()

                        with st.expander("🤖 LLM Internal Reasoning (click to view)"):
                            st.markdown(thinking.replace("<think>", "").replace("</think>", "").strip())

                        st.markdown(rest)
                    else:
                        st.markdown(message)

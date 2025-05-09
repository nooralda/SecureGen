import streamlit as st
from src.ui.scanner_tab import render_scanner_tab
from src.ui.chat_tab import render_chat_tab
from src.ui.rules_tab import render_rules_tab
from src.core.file_utils import cleanup_temp_files
from src.ui.home_tab import render_home_tab
import os




# --- Page Config ---
st.set_page_config(page_title="SecureGen - Vulnerability Scanner", layout="wide")
st.title("🛡️ SecureGen - Vulnerability Scanner")
st.markdown("SecureGen combines Semgrep static analysis with LLM-powered security advice to help you find and fix vulnerabilities in your code more intelligently.")


from src.core.file_utils import cleanup_temp_files

# --- Sidebar Settings ---
st.sidebar.title("⚙️ SecureGen Settings")

# --- Advanced Settings inside Expander ---
with st.sidebar.expander("🔧 Advanced Settings"):
    model_selection = st.selectbox(
        "LLM Model",
        options=[
                "deepseek-r1-distill-llama-70b",
                "allam-2-7b",
                "compound-beta",
                "compound-beta-mini",
                "gemma2-9b-it",
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
                "llama-guard-3-8b",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "meta-llama/llama-4-maverick-17b-128e-instruct",
                "meta-llama/llama-4-scout-17b-16e-instruct",
                "mistral-saba-24b",
                "qwen-qwq-32b"
        ],
        help="Select which LLM model to use for security analysis."
    )

    temperature = st.slider(
        "LLM Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Higher = more creative responses. Lower = more focused and accurate."
    )

    # Semgrep Config Option
    semgrep_config_mode = st.radio(
        "Semgrep Config Mode",
        ("Auto", "Custom Rule"),
        help="Choose between Semgrep’s default rules or a custom rule uploaded in the Rules tab."
    )

    uploaded_rule_file = None
    custom_rule_path = "configs/custom_rules.yml"

    if semgrep_config_mode == "Custom Rule":
        if os.path.exists(custom_rule_path):
            st.success("✅ Custom rule loaded from Rules tab.")
            with open(custom_rule_path, "rb") as f:
                uploaded_rule_file = f.read()
        else:
            st.warning("⚠️ No custom rule found. Please upload a rule in the Rules tab.")



st.sidebar.markdown("---")

# --- Clear Temporary Files Button ---
if st.sidebar.button("🗑️ Clear Uploaded Files"):
    try:
        cleanup_temp_files()
        st.success("Temporary files cleared successfully!")
    except Exception as e:
        st.error(f"❌ Failed to clear temp files: {str(e)}")

st.sidebar.markdown("---")

st.sidebar.markdown("Developed with ❤️ by SecureGen Team")


# --- Tabs ---
tab0, tab1, tab2, tab3= st.tabs(["🏠 Home", "📊 Scanner", "💬 Chat", "📋 Rules"])

with tab0:
    render_home_tab()

with tab1:
    render_scanner_tab(model_selection, temperature, semgrep_config_mode, uploaded_rule_file)



with tab2:
    render_chat_tab(model_selection, temperature)

with tab3:
    render_rules_tab()

# with tab4:
#     render_quiz_tab()



st.markdown("---")
st.markdown("© 2025 SecureGen | Group 1 Project | Developed to enhance secure coding practices using AI and static analysis tools.")


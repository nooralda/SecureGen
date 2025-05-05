import streamlit as st
import os
import time
import base64
import pandas as pd

from src.core.scan import run_semgrep_scan
from src.core.analysis import analyze_security
from src.core.file_utils import save_uploaded_file, save_code_to_temp_file, generate_report

def render_scanner_tab(model_selection, temperature, semgrep_config_mode, uploaded_rule_file):
    st.header("📊 Scanner")

    scan_mode = st.radio(
        "Choose scan method:",
        ("📤 Upload a File", "📤 Upload Multiple Files", "📝 Paste Code Manually")
    )

    code_contents = []
    file_paths = []

    if scan_mode == "📤 Upload a File":
        uploaded_file = st.file_uploader(
            "Upload a code file",
            type=["py", "js", "java", "cpp", "c", "cs", "php", "rb", "go", "ts", "html", "css", "sql"]
        )

        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            file_path = save_uploaded_file(uploaded_file)
            with open(file_path, "r", encoding="utf-8") as f:
                code_contents.append(f.read())
                file_paths.append(file_path)

    elif scan_mode == "📤 Upload Multiple Files":
        uploaded_files = st.file_uploader(
            "Upload multiple code files",
            type=["py", "js", "java", "cpp", "c", "cs", "php", "rb", "go", "ts", "html", "css", "sql"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} files uploaded successfully!")
            for uploaded_file in uploaded_files:
                file_path = save_uploaded_file(uploaded_file)
                with open(file_path, "r", encoding="utf-8") as f:
                    code_contents.append(f.read())
                    file_paths.append(file_path)

    else:  # Paste manually
        pasted_code = st.text_area("Paste your code here:", height=300)
        if pasted_code:
            file_path = save_code_to_temp_file(pasted_code)
            code_contents.append(pasted_code)
            file_paths.append(file_path)

    if file_paths and code_contents:
        if st.button("🔍 Run Scan"):
            try:
                full_report = ""
                total_files = len(file_paths)
                total_issues = 0

                for path, code_content in zip(file_paths, code_contents):
                    st.markdown(f"### 🔍 Scanning {os.path.basename(path)}")

                    # Decide Semgrep config
                    if semgrep_config_mode == "Auto":
                        config_to_use = "auto"
                    elif uploaded_rule_file is not None:
                        custom_rules_path = "temp_uploaded_rules.yml"
                        with open(custom_rules_path, "wb") as f:
                            f.write(uploaded_rule_file.getbuffer())
                        config_to_use = custom_rules_path
                    else:
                        config_to_use = "auto"

                    # Semgrep timing
                    with st.spinner("Running Semgrep..."):
                        start_semgrep = time.time()
                        semgrep_results = run_semgrep_scan(path, config=config_to_use)
                        semgrep_time = time.time() - start_semgrep

                    st.subheader(f"📄 Semgrep Results")
                    st.json(semgrep_results)
                    if "results" in semgrep_results:
                        num_issues = len(semgrep_results["results"])
                        total_issues += num_issues
                        st.info(f"Semgrep found **{num_issues} issue(s)**.")
                    else:
                        st.info("✅ No issues found.")
                    st.markdown(f"🕒 **Semgrep time:** {semgrep_time:.2f} sec")

                    # LLM timing
                    with st.spinner("Running LLM analysis..."):
                        start_llm = time.time()
                        llm_report = analyze_security(semgrep_results, code_content, model_selection, temperature)
                        llm_time = time.time() - start_llm

                    st.subheader("🧠 LLM Analysis")
                    st.write(llm_report)
                    st.markdown(f"🕒 **LLM time:** {llm_time:.2f} sec")

                    # Append to report
                    full_report += generate_report(code_content, llm_report)
                    full_report += "\n\n---\n\n"

                # Scan summary
                st.markdown("---")
                st.subheader("📊 Scan Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Files Scanned", total_files)
                with col2:
                    st.metric("Total Issues", total_issues)

                st.markdown("#### 📈 Issues Distribution")
                summary_df = pd.DataFrame({
                    "Metric": ["Files Scanned", "Issues Found"],
                    "Count": [total_files, total_issues]
                })
                st.bar_chart(summary_df.set_index("Metric"))

                # Report download
                st.markdown("---")
                st.subheader("📄 Download Full Security Report")
                temp_report_path = "temp_full_report.md"
                with open(temp_report_path, "w", encoding="utf-8") as f:
                    f.write(full_report)

                with open(temp_report_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()

                href = f'<a href="data:file/markdown;base64,{b64}" download="SecureGen_Report.md">📥 Download Full Report</a>'
                st.markdown(href, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error during scan: {str(e)}")

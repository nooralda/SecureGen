import streamlit as st
import os
import time
import base64
import pandas as pd
from src.core.severity import assign_severity

from src.core.scan import run_semgrep_scan
from src.core.analysis import analyze_security
from src.core.file_utils import (
    save_uploaded_file,
    save_code_to_temp_file,
    generate_report,
    get_files_from_folder,
    extract_zip_to_temp
)

def render_scanner_tab(model_selection, temperature, semgrep_config_mode, uploaded_rule_file):
    st.header("📊 Scanner")

    scan_mode = st.radio(
        "Choose scan method:",
        (
            "📤 Upload a File",
            "📤 Upload Multiple Files",
            "📝 Paste Code Manually",
            "📁 Upload Repository (ZIP)"
        )
    )

    # === ZIP Repository Mode ===
    if scan_mode == "📁 Upload Repository (ZIP)":
        uploaded_zip = st.file_uploader("Upload a .zip file of the codebase", type=["zip"])
        if uploaded_zip:
            st.success("Repo ZIP uploaded!")
            repo_path = extract_zip_to_temp(uploaded_zip)
            repo_files = get_files_from_folder(repo_path, max_files=1000)

            if not repo_files:
                st.warning("⚠️ No code files found in the uploaded repo.")
                return

            rel_to_abs = {
                os.path.relpath(abs_path, repo_path): abs_path
                for abs_path in repo_files
            }

            selected_rel_path = st.selectbox("Select file to analyze", list(rel_to_abs.keys()))
            selected_abs_path = rel_to_abs[selected_rel_path]
            selected_code = repo_files[selected_abs_path]
            st.code(selected_code, language="java")

            if st.button("🔍 Scan Selected File (Context from Whole Repo)"):
                with st.spinner("⏳ Running Semgrep on entire repo..."):
                    start_scan = time.time()
                    semgrep_results = run_semgrep_scan(repo_path)
                    semgrep_time = round(time.time() - start_scan, 2)

                filtered = {
                    "results": [r for r in semgrep_results.get("results", []) if selected_rel_path in r["path"]]
                }

                file_issues = filtered.get("results", [])
                num_file_issues = len(file_issues)

                st.subheader(f"🔎 Semgrep Results for `{selected_rel_path}`")
                st.json(filtered)
                st.info(f"🔍 Found **{num_file_issues} issues** ({semgrep_time}s)")

                if num_file_issues:
                    st.markdown("### 🚨 Issue List")
                    for i, issue in enumerate(file_issues, 1):
                        rule_id = issue.get("check_id", "unknown")
                        message = issue.get("extra", {}).get("message", "No message")
                        line = issue.get("start", {}).get("line", "?")
                        severity = assign_severity(issue)

                        color = {
                            "Critical": "🔴",
                            "High": "🟠",
                            "Medium": "🟡",
                            "Low": "🟢"
                        }.get(severity, "⚪")

                        st.markdown(
                            f"**{i}. {color} [{severity}]** `{rule_id}` at line {line}: {message}"
                        )

                else:
                    st.success("No issues found in this file!")

                with st.spinner("💬 Analyzing with LLM..."):
                    start_llm = time.time()
                    llm_response = analyze_security(filtered, selected_code, model_selection, temperature)
                    llm_time = round(time.time() - start_llm, 2)

                st.subheader("LLM Analysis")
                st.markdown(f"Time: {llm_time}s")
                if "Fix:" in llm_response:
                    explanation, fix = llm_response.split("Fix:", 1)
                    st.markdown("### 💡 Explanation")
                    st.markdown(explanation.strip())
                    st.markdown("### 🛠 Suggested Fix")
                    st.code(fix.strip(), language="java")
                else:
                    st.write(llm_response)

                st.subheader("📊 Full Repo Scan Summary")
                total_files = len(repo_files)
                total_issues = len(semgrep_results.get("results", []))
                col1, col2 = st.columns(2)
                col1.metric("Total Files", total_files)
                col2.metric("Total Issues", total_issues)

                st.subheader("📄 Selected File Summary")
                col3, col4 = st.columns(2)
                col3.metric("Issues in File", num_file_issues)
                col4.metric("File Path", selected_rel_path)

                summary_df = pd.DataFrame({
                    "Metric": ["Total Files", "Total Issues", "File Issues"],
                    "Count": [total_files, total_issues, num_file_issues]
                })
                st.bar_chart(summary_df.set_index("Metric"))

            return  # skip other scan modes

    # === Other Scan Modes ===
    code_contents = []
    file_paths = []

    if scan_mode == "📤 Upload a File":
        uploaded_file = st.file_uploader("Upload a code file", type=["py", "js", "java", "cpp", "c", "cs", "php", "rb", "go", "ts", "html", "css", "sql"])
        if uploaded_file:
            st.success("File uploaded successfully!")
            path = save_uploaded_file(uploaded_file)
            with open(path, "r", encoding="utf-8") as f:
                code_contents.append(f.read())
                file_paths.append(path)

    elif scan_mode == "📤 Upload Multiple Files":
        uploaded_files = st.file_uploader("Upload multiple code files", type=["py", "js", "java", "cpp", "c", "cs", "php", "rb", "go", "ts", "html", "css", "sql"], accept_multiple_files=True)
        if uploaded_files:
            st.success(f"{len(uploaded_files)} files uploaded successfully!")
            for uploaded_file in uploaded_files:
                path = save_uploaded_file(uploaded_file)
                with open(path, "r", encoding="utf-8") as f:
                    code_contents.append(f.read())
                    file_paths.append(path)

    elif scan_mode == "📝 Paste Code Manually":
        pasted_code = st.text_area("Paste your code here:", height=300)
        if pasted_code:
            path = save_code_to_temp_file(pasted_code)
            code_contents.append(pasted_code)
            file_paths.append(path)

    if file_paths and code_contents:
        if st.button("🔍 Run Scan"):
            full_report = ""
            total_issues = 0
            total_files = len(file_paths)

            for path, content in zip(file_paths, code_contents):
                with st.spinner(f"Scanning {os.path.basename(path)}..."):
                    config = "auto"
                    if semgrep_config_mode == "Custom" and uploaded_rule_file:
                        custom_path = "temp_uploaded_rules.yml"
                        with open(custom_path, "wb") as f:
                            f.write(uploaded_rule_file.getbuffer())
                        config = custom_path

                    start = time.time()
                    results = run_semgrep_scan(path, config=config)
                    scan_time = round(time.time() - start, 2)

                issues = results.get("results", [])
                issue_count = len(issues)
                total_issues += issue_count

                st.subheader(f"📄 Semgrep Results for {os.path.basename(path)}")
                st.json(results)  # Show full Semgrep output
                st.info(f"Found {issue_count} issues (⏱️ {scan_time}s)")


                if issue_count:
                    st.markdown("### 🚨 Issue List")
                    for i, issue in enumerate(issues, 1):
                        rule_id = issue.get("check_id", "unknown")
                        message = issue.get("extra", {}).get("message", "No message")
                        line = issue.get("start", {}).get("line", "?")
                        severity = assign_severity(issue)

                        color = {
                            "Critical": "🔴",
                            "High": "🟠",
                            "Medium": "🟡",
                            "Low": "🟢"
                        }.get(severity, "⚪")

                        st.markdown(f"**{i}. {color} [{severity}]** `{rule_id}` at line {line}: {message}")

                else:
                    st.success("No issues found in this file!")

                with st.spinner("Analyzing with LLM..."):
                    start = time.time()
                    llm_response = analyze_security(results, content, model_selection, temperature)
                    llm_time = round(time.time() - start, 2)

                st.subheader(" LLM Analysis")
                st.markdown(f"Time: {llm_time}s")
                if "Fix:" in llm_response:
                    explanation, fix = llm_response.split("Fix:", 1)
                    st.markdown("### 💡 Explanation")
                    st.markdown(explanation.strip())
                    st.markdown("### 🛠 Suggested Fix")
                    st.code(fix.strip(), language="java")
                else:
                    st.write(llm_response)

                full_report += generate_report(content, llm_response) + "\n\n---\n\n"

            st.subheader("📊 Scan Summary")
            col1, col2 = st.columns(2)
            col1.metric("Files Scanned", total_files)
            col2.metric("Total Issues", total_issues)

            df = pd.DataFrame({"Metric": ["Files", "Issues"], "Count": [total_files, total_issues]})
            st.bar_chart(df.set_index("Metric"))

            st.subheader("📄 Download Report")
            with open("temp_full_report.md", "w", encoding="utf-8") as f:
                f.write(full_report)
            with open("temp_full_report.md", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:file/markdown;base64,{b64}" download="SecureGen_Report.md">📥 Download</a>'
            st.markdown(href, unsafe_allow_html=True)

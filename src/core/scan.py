import subprocess, json

def run_semgrep_scan(path, config="auto", metrics=True):
    """
    Run semgrep on a file.
    - config: "auto" or path/to/rules.yml
    - metrics: True/False
    """
    output = "results.json"
    cmd = ["semgrep", "--json", "--output", output]
    if not metrics:
        cmd.append("--metrics=off")
    cmd += ["--config", config, path]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Semgrep error:\n{proc.stderr}")

    with open(output) as f:
        return json.load(f)

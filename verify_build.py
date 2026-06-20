import subprocess
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Mapping of code files to corresponding E2E test files
MAPPING = {
    "scratch/test_e2e_curation.py": ["scratch/test_e2e_curation.py"],
    "scratch/test_e2e_collections.py": ["scratch/test_e2e_collections.py"],
    "scratch/test_e2e_filters.py": ["scratch/test_e2e_filters.py"],
    "scratch/test_e2e_modal.py": ["scratch/test_e2e_modal.py"],
    "curator.html": ["scratch/test_e2e_curation.py"],
    "static/js/lego_detail_admin.js": ["scratch/test_e2e_curation.py"],
    "static/js/lego_render_admin.js": ["scratch/test_e2e_curation.py"],
    "static/js/lego_collections.js": ["scratch/test_e2e_collections.py"],
    "static/js/lego_filters.js": ["scratch/test_e2e_filters.py"],
    "static/js/lego_detail_client.js": ["scratch/test_e2e_modal.py"],
    "static/js/lego_render_client.js": ["scratch/test_e2e_modal.py"],
    "static/js/lego_lead_capture.js": ["scratch/test_e2e_modal.py"],
}

def run_git_command(args):
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return []

def get_changed_files():
    # Verify if inside a git repository
    is_git = False
    try:
        res = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
        if res.returncode == 0 and "true" in res.stdout.lower():
            is_git = True
    except Exception:
        pass
        
    if not is_git:
        return None

    changed = set()
    # 1. Staged changes
    changed.update(run_git_command(["diff", "--cached", "--name-only"]))
    # 2. Unstaged changes
    changed.update(run_git_command(["diff", "--name-only"]))
    
    # 3. Unpushed commits in current branch compared to upstream
    upstream_exists = False
    try:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "@{u}"], capture_output=True, text=True)
        if res.returncode == 0:
            upstream_exists = True
    except Exception:
        pass
        
    if upstream_exists:
        changed.update(run_git_command(["log", "@{u}..HEAD", "--name-only"]))
    else:
        origin_main_exists = False
        try:
            res = subprocess.run(["git", "rev-parse", "--verify", "origin/main"], capture_output=True)
            if res.returncode == 0:
                origin_main_exists = True
        except Exception:
            pass
            
        if origin_main_exists:
            changed.update(run_git_command(["log", "origin/main..HEAD", "--name-only"]))
        else:
            # Fallback to files changed in last commit
            changed.update(run_git_command(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]))
            
    # Normalize paths
    normalized = set()
    for f in changed:
        f_norm = f.replace("\\", "/").strip().strip('"').strip("'")
        if f_norm:
            normalized.add(f_norm)
            
    return normalized

def is_relevant_file(filepath):
    # Skip documentation, logs, testing assets, installation scripts or batch files
    ignored_exts = ('.md', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.spec', '.bat', '.iss', '.gitignore', '.bak', '.sample')
    if filepath.lower().endswith(ignored_exts):
        return False
    # Ignore dotfiles/folders like .git, .github, .agents, .gemini
    parts = filepath.replace("\\", "/").split("/")
    if any(p.startswith('.') for p in parts):
        return False
    return True

def run_test(script_path):
    print(f"Running E2E test suite: {script_path}...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode == 0:
        print(f"[PASS] {script_path} completed successfully.")
        return True, result.stdout
    else:
        print(f"[FAIL] {script_path} failed (exit code {result.returncode}).")
        return False, result.stdout + "\n" + result.stderr

def main():
    default_test_files = [
        "scratch/test_e2e_curation.py",
        "scratch/test_e2e_collections.py",
        "scratch/test_e2e_filters.py",
        "scratch/test_e2e_modal.py"
    ]
    
    print("==================================================")
    print("    AUTOMATED SYSTEM PRE-DEPLOYMENT VERIFICATION  ")
    print("==================================================")
    print(f"Working Directory: {os.getcwd()}")
    
    changed_files = get_changed_files()
    
    selected_tests = []
    reason = ""
    
    if changed_files is None:
        selected_tests = default_test_files
        reason = "Not inside a Git repository. Running all E2E test suites."
    elif not changed_files:
        selected_tests = default_test_files
        reason = "No Git changes detected (clean repository/manual execution). Running all E2E test suites."
    else:
        relevant_changed = {f for f in changed_files if is_relevant_file(f)}
        if not relevant_changed:
            print("No code changes detected (only documentation, assets, or ignored files modified).")
            print("Skipping E2E tests.")
            print("==================================================")
            sys.exit(0)
            
        print("Detected modified files in changeset:")
        for f in sorted(relevant_changed):
            print(f"  - {f}")
            
        unmapped_files = []
        tests_to_run = set()
        for f in relevant_changed:
            mapped = False
            for pattern, target_tests in MAPPING.items():
                if f == pattern:
                    tests_to_run.update(target_tests)
                    mapped = True
                    break
            if not mapped:
                unmapped_files.append(f)
                
        if unmapped_files:
            selected_tests = default_test_files
            reason = "Changes detected in core or unmapped files:\n" + "\n".join(f"  - {uf}" for uf in unmapped_files) + "\nRunning all E2E test suites."
        else:
            selected_tests = sorted(list(tests_to_run))
            reason = "Selective E2E testing based on modified components."
            
    print("--------------------------------------------------")
    print(f"Selection Reason:\n{reason}")
    print(f"Test suites to run: {', '.join(selected_tests)}")
    print("--------------------------------------------------")
    print("Running Playwright headless suites...")
    print("--------------------------------------------------")
    
    all_passed = True
    failures = []
    
    for tf in selected_tests:
        if not os.path.exists(tf):
            # Fallback path if run from scratch directory or root
            alt_path = os.path.join("scratch", os.path.basename(tf))
            if os.path.exists(alt_path):
                tf = alt_path
            else:
                print(f"[WARN] Test script not found: {tf}. Skipping...")
                continue
                
        passed, output = run_test(tf)
        if not passed:
            all_passed = False
            failures.append((tf, output))
            
    print("\n=================== SUMMARY ======================")
    if all_passed:
        print("[SUCCESS] All selected E2E test suites passed successfully!")
        print("Codebase is stable.")
        sys.exit(0)
    else:
        print("[FAILURE] The following test suites failed:")
        for tf, log in failures:
            print(f"\n--- FAILURE LOG: {tf} ---")
            lines = log.splitlines()
            if len(lines) > 50:
                print("\n".join(lines[:20]))
                print(f"\n... [TRUNCATED {len(lines)-40} LINES] ...\n")
                print("\n".join(lines[-20:]))
            else:
                print(log)
        sys.exit(1)

if __name__ == "__main__":
    main()


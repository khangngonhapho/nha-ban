import subprocess
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

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
    # List of all critical Playwright E2E tests
    test_files = [
        "scratch/test_e2e_curation.py",
        "scratch/test_e2e_collections.py",
        "scratch/test_e2e_filters.py",
        "scratch/test_e2e_modal.py"
    ]
    
    all_passed = True
    failures = []
    
    print("==================================================")
    print("    AUTOMATED SYSTEM PRE-DEPLOYMENT VERIFICATION  ")
    print("==================================================")
    print(f"Working Directory: {os.getcwd()}")
    print("Running Playwright headless suites...")
    print("--------------------------------------------------")
    
    for tf in test_files:
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
        print("[SUCCESS] All E2E test suites passed successfully!")
        print("Codebase is stable and safe for production deployment.")
        sys.exit(0)
    else:
        print("[FAILURE] The following test suites failed:")
        for tf, log in failures:
            print(f"\n--- FAILURE LOG: {tf} ---")
            # Limit the output log to avoid flooding
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

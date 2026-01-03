import subprocess
import os
from datetime import datetime
import sys

# ============================================================
# CONFIG
# ============================================================
PROJECT_PATH = r"C:\Users\rana\Desktop\WhatApp bussines"
GITHUB_URL = "https://github.com/vakhileshni/test.git"
COMMIT_MESSAGE = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

GIT = r"C:\Program Files\Git\cmd\git.exe"
BFG_JAR = r"C:\tools\bfg-1.14.0.jar"  # path to BFG jar

# Files where secrets may appear
SECRET_FILES = [
    r"backend/env.example",
    r"backend/main.py",
    r"backend/services/whatsapp_service.py"
]

# Secrets to replace
SECRETS_REPLACEMENTS = {
    "YOUR_TWILIO_SID": "TWILIO_SID_PLACEHOLDER",
    "YOUR_TWILIO_AUTH_TOKEN": "TWILIO_TOKEN_PLACEHOLDER"
}

SECRETS_TXT_PATH = os.path.join(PROJECT_PATH, "secrets.txt")

# ============================================================
# UTILITIES
# ============================================================
def run_cmd(cmd, ignore_errors=False):
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip() and not ignore_errors:
        print(f"❌ {result.stderr.strip()}")
    return result.returncode, result.stdout.strip()


def check_git():
    if not os.path.exists(GIT):
        print("❌ Git executable not found:", GIT)
        return False
    code, out = run_cmd([GIT, "--version"])
    if code == 0:
        print(f"✅ {out}")
        return True
    print("❌ Git exists but cannot be executed.")
    return False


def sanitize_current_files():
    print("🔒 Sanitizing secrets in current files...")
    for file_path in SECRET_FILES:
        full_path = os.path.join(PROJECT_PATH, file_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            for secret, placeholder in SECRETS_REPLACEMENTS.items():
                content = content.replace(secret, placeholder)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
    print("✅ Secrets sanitized in current files\n")


def create_secrets_txt():
    print("📄 Creating secrets.txt for BFG...")
    with open(SECRETS_TXT_PATH, "w", encoding="utf-8") as f:
        for secret, placeholder in SECRETS_REPLACEMENTS.items():
            f.write(f"{secret}==>{placeholder}\n")
    print(f"✅ secrets.txt created at {SECRETS_TXT_PATH}\n")


def sanitize_history_with_bfg():
    print("🧹 Sanitizing commit history using BFG...")
    cmd = ["java", "-jar", BFG_JAR, f"--replace-text", SECRETS_TXT_PATH]
    code, _ = run_cmd(cmd)
    if code != 0:
        print("❌ BFG failed")
        sys.exit(1)
    print("✅ Commit history sanitized\n")


def git_clean_and_push():
    print("🧹 Cleaning git refs and pushing...")
    run_cmd([GIT, "reflog", "expire", "--expire=now", "--all"])
    run_cmd([GIT, "gc", "--prune=now", "--aggressive"])
    run_cmd([GIT, "add", "."])
    run_cmd([GIT, "commit", "-m", COMMIT_MESSAGE], ignore_errors=True)
    run_cmd([GIT, "branch", "-M", "main"])
    if run_cmd([GIT, "remote", "get-url", "origin"], ignore_errors=True)[0] != 0:
        run_cmd([GIT, "remote", "add", "origin", GITHUB_URL])
    else:
        run_cmd([GIT, "remote", "set-url", "origin", GITHUB_URL])
    # Force push
    code, _ = run_cmd([GIT, "push", "--force", "-u", "origin", "main"])
    if code != 0:
        print("❌ Push failed")
        sys.exit(1)
    print("✅ Project pushed to GitHub successfully!\n")


# ============================================================
# MAIN
# ============================================================
print("\n" + "="*60)
print("🚀 WhatsApp Business Project - GitHub Push Script")
print("="*60 + "\n")

os.chdir(PROJECT_PATH)
print(f"📁 Changed directory to: {PROJECT_PATH}\n")

if not check_git():
    sys.exit(1)

sanitize_current_files()
create_secrets_txt()
sanitize_history_with_bfg()
git_clean_and_push()

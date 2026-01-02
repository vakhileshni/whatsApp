import subprocess
import os
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
PROJECT_PATH = r"C:\Users\rana\Desktop\WhatApp bussines"
GITHUB_URL = "https://github.com/vakhileshni/ak.git"
COMMIT_MESSAGE = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Absolute Git path (CRITICAL for Windows + venv)
GIT = r"C:\Program Files\Git\cmd\git.exe"

# ============================================================
# UTILITIES
# ============================================================
def git_cmd(args, ignore_errors=False):
    """Run git command using absolute git.exe"""
    cmd = [GIT] + args
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


def check_git_installed():
    if not os.path.exists(GIT):
        print("❌ Git executable not found.")
        print("Expected path:", GIT)
        return False

    code, out = git_cmd(["--version"])
    if code == 0:
        print(f"✅ {out}\n")
        return True

    print("❌ Git exists but cannot be executed.")
    return False


def has_changes():
    _, out = git_cmd(["status", "--porcelain"])
    return bool(out)


def remote_exists():
    code, _ = git_cmd(["remote", "get-url", "origin"], ignore_errors=True)
    return code == 0


# ============================================================
# MAIN
# ============================================================
print("\n" + "=" * 60)
print("🚀 WhatsApp Business Project - GitHub Push Script")
print("=" * 60 + "\n")

# Change directory
os.chdir(PROJECT_PATH)
print(f"📁 Changed directory to: {PROJECT_PATH}\n")

# Check Git
if not check_git_installed():
    exit(1)

# 1️⃣ Initialize repo
if not os.path.exists(os.path.join(PROJECT_PATH, ".git")):
    print("📦 Initializing Git repository...")
    code, _ = git_cmd(["init"])
    if code != 0:
        exit(1)
    print("✅ Git repository initialized\n")
else:
    print("✅ Git repository already exists\n")

# 2️⃣ Configure user
print("👤 Checking Git user configuration...")
_, name = git_cmd(["config", "user.name"], ignore_errors=True)
if not name:
    git_cmd(["config", "user.name", "WhatsApp Business"])

_, email = git_cmd(["config", "user.email"], ignore_errors=True)
if not email:
    git_cmd(["config", "user.email", "whatsapp@business.local"])
print()

# 3️⃣ Add files
print("📝 Adding files...")
code, _ = git_cmd(["add", "."])
if code != 0:
    exit(1)

# 4️⃣ Commit
if has_changes():
    print(f"💾 Committing: {COMMIT_MESSAGE}")
    git_cmd(["commit", "-m", COMMIT_MESSAGE], ignore_errors=True)
else:
    print("ℹ️ No changes to commit")

print()

# 5️⃣ Set branch
git_cmd(["branch", "-M", "main"], ignore_errors=True)

# 6️⃣ Remote
print("🔗 Configuring remote...")
if remote_exists():
    git_cmd(["remote", "set-url", "origin", GITHUB_URL])
else:
    git_cmd(["remote", "add", "origin", GITHUB_URL])
print(f"✅ Remote set to {GITHUB_URL}\n")

# 7️⃣ Push
print("⬆️ Pushing to GitHub...\n")
code, _ = git_cmd(["push", "-u", "origin", "main"], ignore_errors=True)
if code != 0:
    print("⚠️ Normal push failed. Trying force push...")
    code, _ = git_cmd(["push", "--force", "-u", "origin", "main"])
    if code != 0:
        print("❌ Push failed")
        exit(1)

print("\n" + "=" * 60)
print("✅ Project pushed to GitHub successfully!")
print("=" * 60)
print(f"🌐 Repo: {GITHUB_URL}")
print(f"📝 Commit: {COMMIT_MESSAGE}")
print("=" * 60)

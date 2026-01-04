import subprocess
import os
import sys
import shutil
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================
# CONFIG
# ============================================================
PROJECT_PATH = r"C:\Users\rana\Desktop\WhatApp bussines"
GITHUB_URL = "https://github.com/vakhileshni/whatsApp.git"
COMMIT_MESSAGE = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Added Dockerfile, EC2 deployment config, and updated features"

# ============================================================
# GIT DETECTION
# ============================================================
def find_git():
    """Find Git executable on Windows"""
    # Try common Git installation paths on Windows
    common_paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]
    
    # First try to find git in PATH
    git_path = shutil.which("git")
    if git_path:
        return git_path
    
    # Try common installation paths
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Try where command on Windows
    try:
        result = subprocess.run("where git", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

GIT = find_git()
if not GIT:
    GIT = "git"  # Fallback to PATH

# ============================================================
# UTILITIES
# ============================================================
def git_cmd(args, ignore_errors=False):
    """Run git command"""
    # Use git directly from PATH (it's working)
    cmd = "git " + " ".join(f'"{arg}"' if " " in str(arg) else str(arg) for arg in args)
    
    # Preserve environment PATH
    env = os.environ.copy()
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip() and not ignore_errors:
        print(f"❌ {result.stderr.strip()}")

    return result.returncode, result.stdout.strip()


def check_git_installed():
    # Preserve environment PATH
    env = os.environ.copy()
    result = subprocess.run("git --version", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if result.returncode == 0:
        print(f"✅ {result.stdout.strip()}\n")
        return True
    
    print("❌ Git is not installed or not found in PATH.")
    print("📋 Troubleshooting steps:")
    print("   1. Make sure Git is installed: https://git-scm.com/downloads")
    print("   2. Restart your terminal/command prompt after installing Git")
    print("   3. Check if Git is in PATH: Open Command Prompt and type 'git --version'")
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

# 4️⃣ Check for changes before committing
has_uncommitted = has_changes()
if has_uncommitted:
    print(f"💾 Committing: {COMMIT_MESSAGE}")
    code, _ = git_cmd(["commit", "-m", COMMIT_MESSAGE])
    if code == 0:
        print("✅ Changes committed successfully\n")
    else:
        print("⚠️ Commit failed, but continuing...\n")
else:
    print("ℹ️ No changes to commit\n")

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
code, _ = git_cmd(["push", "-u", "origin", "main"])
if code != 0:
    print("⚠️ Push failed. This might be due to:")
    print("   1. Authentication issues (use GitHub credentials or SSH key)")
    print("   2. Remote branch has commits not in local branch")
    print("   3. Network connectivity issues")
    print("\n💡 Try running manually:")
    print(f"   git push -u origin main")
    print("\n❌ Push failed - please check the error above")
    exit(1)

print("\n" + "=" * 60)
print("✅ Project pushed to GitHub successfully!")
print("=" * 60)
print(f"🌐 Repo: {GITHUB_URL}")
print(f"📝 Commit: {COMMIT_MESSAGE}")
print("=" * 60)

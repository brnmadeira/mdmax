#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MdMax Repository Monitor
Tracks GitHub activity and downloads in real-time
"""

import json
import requests
import sys
import os
from pathlib import Path
from datetime import datetime
from time import sleep

# Fix encoding on Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

REPO = "brnmadeira/mdmax"
GITHUB_API = f"https://api.github.com/repos/{REPO}"
STATE_FILE = Path.home() / ".mdmax" / "monitor_state.json"

def load_state():
    """Load previous state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "stars": 0,
        "forks": 0,
        "issues": 0,
        "watchers": 0,
        "last_check": None
    }

def save_state(state):
    """Save current state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_check"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_repo_stats():
    """Get current repository stats"""
    try:
        response = requests.get(GITHUB_API, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "issues": data.get("open_issues_count", 0),
                "watchers": data.get("watchers_count", 0),
            }
    except:
        pass
    return None

def check_updates():
    """Check for updates and report changes"""
    old_state = load_state()
    new_stats = get_repo_stats()

    if not new_stats:
        print("❌ Could not fetch repository data")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n[STATS] MdMax Repository Status - {timestamp}")
    print("=" * 50)

    # Check stars
    if new_stats["stars"] > old_state["stars"]:
        diff = new_stats["stars"] - old_state["stars"]
        print(f"[STARS] NEW: +{diff} (Total: {new_stats['stars']})")
    else:
        print(f"[STARS] Total: {new_stats['stars']}")

    # Check forks
    if new_stats["forks"] > old_state["forks"]:
        diff = new_stats["forks"] - old_state["forks"]
        print(f"[FORKS] NEW: +{diff} (Total: {new_stats['forks']})")
    else:
        print(f"[FORKS] Total: {new_stats['forks']}")

    # Check issues
    if new_stats["issues"] > old_state["issues"]:
        diff = new_stats["issues"] - old_state["issues"]
        print(f"[ISSUES] NEW: +{diff} (Total: {new_stats['issues']})")
    else:
        print(f"[ISSUES] Open: {new_stats['issues']}")

    # Check watchers
    if new_stats["watchers"] > old_state["watchers"]:
        diff = new_stats["watchers"] - old_state["watchers"]
        print(f"[WATCHERS] NEW: +{diff} (Total: {new_stats['watchers']})")
    else:
        print(f"[WATCHERS] Total: {new_stats['watchers']}")

    print("=" * 50)
    print(f"Repository: https://github.com/{REPO}")
    print("")

    # Save new state
    save_state(new_stats)

def monitor_continuous(interval=300):
    """Continuous monitoring (every 5 minutes)"""
    print(f"🔍 Starting MdMax Repository Monitor")
    print(f"📍 Repository: https://github.com/{REPO}")
    print(f"⏱️ Checking every {interval} seconds\n")

    while True:
        try:
            check_updates()
            print(f"⏳ Next check in {interval} seconds...\n")
            sleep(interval)
        except KeyboardInterrupt:
            print("\n✅ Monitor stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            sleep(60)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        monitor_continuous(interval)
    else:
        check_updates()

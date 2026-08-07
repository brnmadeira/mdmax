#!/usr/bin/env python3
"""
MdMax Skill Runner for Claude Code
Enables /mdmax command in Claude
"""

import sys
import subprocess
import json
from pathlib import Path

def run_mdmax_command(args):
    """Execute MdMax command"""
    try:
        result = subprocess.run(
            ["mdmax"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to execute MdMax"
        }

if __name__ == "__main__":
    # Parse arguments
    # Usage: python mdmax-runner.py convert file.pdf
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: mdmax-runner.py <command> [args...]",
            "commands": ["convert", "stats", "dashboard", "config", "init"]
        }))
        sys.exit(1)
    
    # Execute
    result = run_mdmax_command(sys.argv[1:])
    print(json.dumps(result, indent=2))

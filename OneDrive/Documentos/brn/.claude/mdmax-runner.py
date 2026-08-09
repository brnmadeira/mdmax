#!/usr/bin/env python3
"""
MdMax Skill Runner for Claude Code
Enables /mdmax command in Claude
"""

import sys
import subprocess
import json
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any

# Allowed subcommands (whitelist)
ALLOWED_COMMANDS = {"convert", "dashboard", "config", "init", "version"}

# Paths that cannot be overwritten (security allowlist)
PROTECTED_PATHS = {
    ".claude",
    ".git",
    ".env",
    "node_modules",
    "venv",
    ".venv"
}

# Timeout configurável via env var
DEFAULT_TIMEOUT = int(os.getenv("MDMAX_TIMEOUT", "120"))

def validate_args(args: List[str]) -> bool:
    """Validate command and arguments for security"""
    if not args:
        raise ValueError("No command specified")

    command = args[0]
    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"Unknown command: {command}. Allowed: {', '.join(ALLOWED_COMMANDS)}")

    # Check for --output argument and validate it doesn't escape allowed directory
    if "--output" in args or "-o" in args:
        try:
            idx = args.index("--output") if "--output" in args else args.index("-o")
            if idx + 1 >= len(args):
                raise ValueError("--output requires a value")

            output_path = Path(args[idx + 1]).resolve()
            cwd = Path.cwd().resolve()

            # Ensure output is within current working directory
            try:
                output_path.relative_to(cwd)
            except ValueError:
                raise ValueError(f"Output path must be within {cwd}")

            # Check against protected paths
            for part in output_path.parts:
                if part in PROTECTED_PATHS:
                    raise ValueError(f"Cannot write to protected path: {part}")
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid output path: {e}")

    return True

def run_mdmax_command(args: List[str]) -> Dict[str, Any]:
    """Execute MdMax command"""
    try:
        # Validate arguments first
        validate_args(args)

        # Check if mdmax binary exists (prevent binary planting)
        mdmax_path = shutil.which("mdmax")
        if not mdmax_path:
            raise FileNotFoundError("mdmax binary not found in PATH")

        result = subprocess.run(
            [mdmax_path] + args,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            encoding="utf-8",
            errors="replace"
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "message": "Command executed successfully" if result.returncode == 0 else "Command failed"
        }
    except ValueError as e:
        # Validation error (command not allowed, path escaping, etc)
        return {
            "status": "error",
            "error": "validation_failed",
            "message": str(e)
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "timeout",
            "message": "MdMax command timed out after 30 seconds"
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error": "not_found",
            "message": "MdMax command not found. Install with: pip install git+https://github.com/brnmadeira/mdmax.git"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": "execution_failed",
            "message": f"Failed to execute MdMax: {str(e)}"
        }

if __name__ == "__main__":
    # Parse arguments
    # Usage: python mdmax-runner.py convert file.pdf
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: mdmax-runner.py <command> [args...]",
            "commands": ["convert", "dashboard", "config", "init", "version"]
        }))
        sys.exit(1)
    
    # Execute
    result = run_mdmax_command(sys.argv[1:])
    print(json.dumps(result, indent=2))

    # Exit with proper code: pass through mdmax's return code
    # This allows shell/CI/hooks to detect success vs failure
    if "returncode" in result:
        sys.exit(result["returncode"])
    elif result.get("status") == "error":
        sys.exit(1)
    else:
        sys.exit(0)

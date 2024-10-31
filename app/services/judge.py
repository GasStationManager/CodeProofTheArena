import subprocess
import tempfile
import os
import re

def check_lean_proof(challenge: dict, submission: dict) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a temporary Lean file
        with open(os.path.join(tmpdir, "code.lean"), "w") as f:
            f.write(f"""
{challenge['function_signature']}
{submission['code']}
""")
        with open(os.path.join(tmpdir, "proof.lean"), "w") as f:
            f.write(f"""
{challenge['function_signature']}
{submission['code']}

{challenge['theorem_signature']}
{submission['proof']}
""")
        for fname in ['code.lean', 'proof.lean']:
            # Run Lean 4 on the temporary file
            result = subprocess.run(["lean", fname], cwd=tmpdir, capture_output=True, text=True)
        
            # Check if Lean 4 succeeded (return code 0 means success)
            is_correct = result.returncode == 0
        
            # Extract error messages if the proof failed
            error_message = ""
            error_lines = result.stderr.split('\n') + result.stdout.split('\n')
            for line in error_lines:
                error_message += line + "\n"
                if "error:" in line or "warning: declaration uses 'sorry'" in line:
                    is_correct=False
            if not is_correct:
              break
        
        return {
            "is_correct": is_correct,
            "feedback": error_message.strip() if error_message else "Proof checked successfully!"
        }

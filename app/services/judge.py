import subprocess
import tempfile
import os
import re

def check_lean_proof(challenge: dict, submission: dict) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary Lean files
        function_sig=challenge['function_signature']
        if 'import' not in function_sig:
            function_sig='import Mathlib\n\n'+function_sig
        codef=os.path.join(tmpdir, "code.lean")
        with open(codef, "w") as f:
            f.write(f"""
{function_sig}
{submission['code']}
""")
        prooff=os.path.join(tmpdir, "proof.lean")
        with open(prooff, "w") as f:
            f.write(f"""
{function_sig}
{submission['code']}

{challenge['theorem_signature']}
{submission['proof']}
""")
        proof2f=None
        if challenge.get('theorem2_signature') and submission.get('proof2'):
            proof2f=os.path.join(tmpdir, "proof2.lean")
            with open(proof2f, "w") as f:
                f.write(f"""
{function_sig}
{submission['code']}
""")
                f.write(f"\n\n{challenge['theorem2_signature']}\n\n{submission['proof2']}")

        for fname in [codef, prooff]:
            # Run Lean 4 on the temporary file
            result = subprocess.run(["lake","env","lean", fname], capture_output=True, text=True)
        
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

        is_correct2 = None
        error_message2 = None
        if challenge.get('theorem2_signature') and submission.get('proof2'):
            result2 = subprocess.run(["lake","env","lean", proof2f], capture_output=True, text=True)
            is_correct2 = result2.returncode == 0
            error_message2 = ""
            error_lines2 = result2.stderr.split('\n') + result2.stdout.split('\n')
            for line in error_lines2:
                error_message2 += line + "\n"
                if "error:" in line or "warning: declaration uses 'sorry'" in line:
                    is_correct2=False


        return {
            "is_correct": is_correct,
            "is_correct2": is_correct2,
            "feedback": error_message.strip() if error_message else "Proof checked successfully!",
            "feedback2": error_message2.strip() if error_message2 else None
        }

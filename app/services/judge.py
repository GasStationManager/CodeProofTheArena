import subprocess
import tempfile
import os
import re





def check_lean_proof(challenge: dict, submission: dict) -> dict:
    with tempfile.TemporaryDirectory(dir='temp') as tmpdir:
        # Create temporary Lean files
        print('created temp directory ', tmpdir)
        function_sig=challenge['function_signature']
        if 'import' not in function_sig:
            function_sig='import Mathlib\n\n'+function_sig


        targf=os.path.join(tmpdir, "target.lean")
        if function_sig.strip().endswith(':='):
            func_body='sorry\n'
        else:
            func_body=':=sorry\n'
        thm_body=':=sorry\n'
        if challenge['theorem_signature'].strip().endswith(':='): thm_body='sorry\n'
        with open(targf, "w") as f:
            f.write(f"""
{function_sig}
{func_body}
{challenge['theorem_signature']}
{thm_body}
""")
        print('finished writing to '+targf)

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
            targ2f=os.path.join(tmpdir, "target2.lean")
            thm2_body='sorry\n' if challegne['theorem2_signature'].strip().endswith(':=') else ':=sorry\n'
            with open(targ2f,'w') as f:
                f.write(f"""
{function_sig}
{func_body}
{challenge['theorem2_signature']}
{thm2_body}
""")
            proof2f=os.path.join(tmpdir, "proof2.lean")
            with open(proof2f, "w") as f:
                f.write(f"""
{function_sig}
{submission['code']}
""")
                f.write(f"\n\n{challenge['theorem2_signature']}\n\n{submission['proof2']}")

        def compile (fname):
            # compile on the temporary file
            assert fname.endswith('.lean')
            ofname=fname[:-4]+'olean'
            result = subprocess.run(["lake","env","lean",'-o',ofname, fname], capture_output=True, text=True)
            # Check if Lean 4 succeeded (return code 0 means success)
            is_correct = result.returncode == 0
            return is_correct, result.stderr + result.stdout

        def compare(targf, subf):
            for f in [targf,subf]:
              r,err=compile(f)
              if not r:
                err=f"Compilation error for {f}:\n"+err
                return r,err
            otarg=targf[:-4]+'olean'
            osub=subf[:-4]+'olean'
            result=subprocess.run(["lake","env","safe_verify",otarg,osub],capture_output=True,text=True)
            is_correct = result.returncode==0
            return is_correct, result.stderr+result.stdout

        is_correct, error_message = compare(targf, prooff)
        

        is_correct2 = None
        error_message2 = None
        if challenge.get('theorem2_signature') and submission.get('proof2'):
            is_correct2,error_messag2=compare(targ2f,proof2f)

        return {
            "is_correct": is_correct,
            "is_correct2": is_correct2,
            "feedback": error_message.strip() if error_message else "Proof checked successfully!",
            "feedback2": error_message2.strip() if error_message2 else None
        }

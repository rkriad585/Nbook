import sys
import io
import os
import subprocess
import base64

# Global State
PYTHON_GLOBALS = {}

def get_variables():
    vars_list = []
    for k, v in PYTHON_GLOBALS.items():
        if not k.startswith('_') and k not in ['sys', 'os', 'io', 'base64', 'plt', 'get_ipython']:
            val_type = type(v).__name__
            val_str = str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
            vars_list.append({"name": k, "type": val_type, "value": val_str})
    return vars_list

def run_python_stateful(code_str):
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = buffer
    
    # Plotting Support Injection
    plot_patch = """
import matplotlib.pyplot as plt
import io, base64
def _nbook_show():
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    print("NBOOK_IMG:" + base64.b64encode(buf.read()).decode('utf-8'))
    plt.clf()
plt.show = _nbook_show
"""
    
    try:
        if "matplotlib" in code_str and "_nbook_show" not in PYTHON_GLOBALS:
             exec(plot_patch, PYTHON_GLOBALS)

        # Magic Commands
        if code_str.strip().startswith('!'):
            cmd = code_str.strip()[1:]
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
            return {"output": proc.stdout + proc.stderr, "status": "success"}

        # Execution
        try:
            compiled = compile(code_str, '<string>', 'eval')
            result = eval(compiled, PYTHON_GLOBALS)
            if result is not None:
                print(result)
        except SyntaxError:
            exec(code_str, PYTHON_GLOBALS)
            
        output = buffer.getvalue()
        return {"output": output, "status": "success"}
    except Exception as e:
        return {"output": str(e), "status": "error"}
    finally:
        sys.stdout = original_stdout

import subprocess
import sys
from langchain_core.tools import tool

@tool
def python_executor(code: str) -> str:
    """
    Executes a snippet of Python code in an isolated subprocess and returns stdout/stderr.
    Useful for calculations, data analysis, and verifying programmatic logic.
    """
    # Clean possible markdown block formatting emitted by LLMs
    cleaned_code = code.strip()
    if cleaned_code.startswith("```python"):
        cleaned_code = cleaned_code[9:]
    if cleaned_code.startswith("```"):
        cleaned_code = cleaned_code[3:]
    if cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[:-3]
    cleaned_code = cleaned_code.strip()

    try:
        result = subprocess.run(
            [sys.executable, "-c", cleaned_code],
            capture_output=True,
            text=True,
            timeout=15
        )
        output = result.stdout
        error = result.stderr

        if result.returncode != 0:
            return f"Execution Error (Exit Code {result.returncode}):\n{error}"
        
        return output if output.strip() else "Code executed successfully with no stdout."
    except subprocess.TimeoutExpired:
        return "Execution Error: Code execution timed out after 15 seconds."
    except Exception as e:
        return f"Execution Error: {str(e)}"
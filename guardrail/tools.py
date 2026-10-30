"""Sandboxed mock tools: nothing here touches the real system."""
def send_email(to, subject="", body=""): return f"[mock] email sent to {to}"
def read_file(path): return f"[mock] read {path}"
def run_shell(cmd): return f"[mock] would run: {cmd}"
def transfer_funds(to_account, amount): return f"[mock] transferred {amount} to {to_account}"
def query_db(sql): return "[mock] 42 rows"
TOOLS = {f.__name__: f for f in (send_email, read_file, run_shell, transfer_funds, query_db)}


def execute(action):
    fn = TOOLS.get(action.tool)
    if not fn:
        return f"unknown tool {action.tool}"
    try:
        return fn(**action.args)
    except TypeError as e:
        return f"bad arguments: {e}"

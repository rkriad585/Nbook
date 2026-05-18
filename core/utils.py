import os

def get_safe_path(workspace, req_path):
    target = os.path.abspath(os.path.join(workspace, req_path.strip('/')))
    return target if target.startswith(workspace) else None

# monitor/process_actions.py

import psutil

def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.kill()
        return True
    except Exception as e:
        return f"Error: {e}"

def renice_process(pid, nice_value=10):
    try:
        proc = psutil.Process(pid)
        proc.nice(nice_value)
        return True
    except Exception as e:
        return f"Error: {e}"

def suspend_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.suspend()
        return True
    except Exception as e:
        return f"Error: {e}"

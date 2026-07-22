import subprocess
r = subprocess.run(['cmd', '/c', 'echo'], capture_output=True, text=True)
print(r.stdout)

import subprocess, shlex, os, tempfile

def run(cmd: str, cwd: str) -> tuple[int, str]:
    p = subprocess.Popen(shlex.split(cmd), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out, _ = p.communicate()
    return p.returncode, out

def deploy(compose_path: str) -> tuple[bool, str]:
    root = os.path.dirname(compose_path)
    rc, out1 = run("docker compose pull", cwd=root)
    if rc != 0: return False, out1
    rc, out2 = run("docker compose up -d --remove-orphans", cwd=root)
    return (rc == 0), (out1 + "\n" + out2)
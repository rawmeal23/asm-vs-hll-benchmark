"""Assembly vs High-Level Languages: arithmetic performance benchmark (Flask server)."""
import os, platform, re, shutil, statistics, subprocess, sys, time
import psutil
from flask import Flask, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
BENCH, OUT = os.path.join(BASE, "bench"), os.path.join(BASE, "build")
EXE = ".exe" if os.name == "nt" else ""
OPS = ["add", "sub", "mul", "div", "mod"]
os.makedirs(OUT, exist_ok=True)

# Source of the operation itself, shown in the UI and used for the code-complexity metric.
SNIPPETS = {
 "assembly": {
  "add": '__asm__ volatile("addq %2, %0" : "=r"(r) : "0"(x), "r"(y));',
  "sub": '__asm__ volatile("subq %2, %0" : "=r"(r) : "0"(x), "r"(y));',
  "mul": '__asm__ volatile("imulq %2, %0" : "=r"(r) : "0"(x), "r"(y));',
  "div": '__asm__ volatile(\n  "cqto\\n\\t"\n  "idivq %3"\n  : "=a"(q), "=&d"(r) : "a"(x), "r"(y) : "cc");\nresult = q;',
  "mod": '__asm__ volatile(\n  "cqto\\n\\t"\n  "idivq %3"\n  : "=a"(q), "=&d"(r) : "a"(x), "r"(y) : "cc");\nresult = r;'},
 "c": {"add": "r = x + y;", "sub": "r = x - y;", "mul": "r = x * y;", "div": "r = x / y;", "mod": "r = x % y;"},
 "python": {"add": "r = x + y", "sub": "r = x - y", "mul": "r = x * y", "div": "r = x // y", "mod": "r = x % y"},
 "javascript": {"add": "r = x + y;", "sub": "r = x - y;", "mul": "r = x * y;", "div": "r = Math.trunc(x / y);", "mod": "r = x % y;"},
 "java": {"add": "r = x + y;", "sub": "r = x - y;", "mul": "r = x * y;", "div": "r = x / y;", "mod": "r = x % y;"},
}

def build_languages():
    langs = {}
    gcc = shutil.which("gcc")
    if gcc:
        exe = os.path.join(OUT, "bench_c" + EXE)
        r = subprocess.run([gcc, "-O2", "-o", exe, os.path.join(BENCH, "bench.c")], capture_output=True, text=True)
        if r.returncode == 0:
            langs["assembly"] = {"label": "Assembly (x86-64)", "cmd": [exe, "asm"]}
            langs["c"] = {"label": "C (gcc -O2)", "cmd": [exe, "c"]}
        else:
            print("gcc build failed (is this an x86-64 CPU?):", r.stderr)
    langs["python"] = {"label": "Python", "cmd": [sys.executable, os.path.join(BENCH, "bench.py")]}
    if shutil.which("node"):
        langs["javascript"] = {"label": "JavaScript (Node)", "cmd": [shutil.which("node"), os.path.join(BENCH, "bench.js")]}
    if shutil.which("javac") and shutil.which("java"):
        r = subprocess.run(["javac", "-d", OUT, os.path.join(BENCH, "Bench.java")], capture_output=True, text=True)
        if r.returncode == 0:
            langs["java"] = {"label": "Java", "cmd": ["java", "-cp", OUT, "Bench"]}
    return langs

LANGS = build_languages()

def complexity(lang, op):
    code = SNIPPETS[lang][op]
    return {"loc": len([l for l in code.splitlines() if l.strip()]),
            "tokens": len(re.findall(r"\w+|[^\s\w]", code))}

def measure(cmd):
    """Run one benchmark process; return (loop_ms, cpu_percent, peak_memory_mb)."""
    t0 = time.perf_counter()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ps, peak, cpu = psutil.Process(p.pid), 0, 0.0
    while True:
        try:
            mi = ps.memory_info(); peak = max(peak, getattr(mi, "peak_wset", mi.rss))
            ct = ps.cpu_times(); cpu = ct.user + ct.system
        except psutil.Error:
            pass
        if p.poll() is not None: break
        if time.perf_counter() - t0 > 180: p.kill(); raise RuntimeError("timeout")
        time.sleep(0.001)
    out, err = p.communicate()
    wall = time.perf_counter() - t0
    if p.returncode != 0: raise RuntimeError(err.strip() or "runner failed")
    return int(out.strip()) / 1e6, min(100.0 * cpu / wall, 100.0 * (os.cpu_count() or 1)), peak / 1048576

app = Flask(__name__, static_folder="static")

@app.get("/")
def index(): return send_from_directory("static", "index.html")

@app.get("/api/info")
def info():
    return jsonify(languages={k: v["label"] for k, v in LANGS.items()}, operations=OPS, snippets=SNIPPETS,
                   system={"cpu": platform.processor() or platform.machine(), "cores": os.cpu_count(),
                           "os": platform.platform(), "python": platform.python_version()})

@app.post("/api/run")
def run():
    d = request.get_json(force=True)
    op = d.get("operation", "add")
    n = max(1000, min(int(d.get("iterations", 10_000_000)), 300_000_000))
    runs = max(1, min(int(d.get("runs", 5)), 30))
    chosen = [l for l in d.get("languages", []) if l in LANGS]
    if op not in OPS or not chosen: return jsonify(error="Pick an operation and at least one language."), 400
    results = {}
    for lang in chosen:
        t, c, m = [], [], []
        try:
            for _ in range(runs):
                a, b, e = measure(LANGS[lang]["cmd"] + [op, str(n)]); t.append(a); c.append(b); m.append(e)
        except Exception as ex:
            results[lang] = {"label": LANGS[lang]["label"], "error": str(ex)}; continue
        results[lang] = {"label": LANGS[lang]["label"], "times_ms": t, "time_ms": statistics.mean(t),
                         "time_sd": statistics.stdev(t) if runs > 1 else 0.0,
                         "ns_per_op": statistics.mean(t) * 1e6 / n, "cpu_pct": statistics.mean(c),
                         "mem_mb": statistics.mean(m), **complexity(lang, op)}
    return jsonify(operation=op, iterations=n, runs=runs, results=results)

if __name__ == "__main__":
    print("Available languages:", ", ".join(LANGS)); print("Open http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)

# Assembly vs High-Level Languages – Arithmetic Benchmark

A web app that runs the same loop (add, subtract, multiply, divide, modulo) in Assembly, C, Python, JavaScript and Java,
then charts **execution time, CPU usage, memory usage and code complexity**.

## Setup (once)
1. Install **Python 3.9+** and **GCC** (Windows: MSYS2/MinGW-w64 64-bit, add `gcc` to PATH; Linux: `sudo apt install build-essential`; Mac Intel: Xcode tools).
2. Optional extra languages: **Node.js** (JavaScript) and a **JDK** (Java). Missing ones are greyed out in the app.
3. In this folder run: `pip install -r requirements.txt`

## Run
    python app.py
Open http://127.0.0.1:5000 , pick an operation and languages, click **Run benchmark**. Internet is needed once per page load for the chart library.

## Notes:
- Assembly is x86-64 inline assembly (GCC syntax). It will not build on ARM (Apple Silicon, Raspberry Pi); use an Intel/AMD PC.
- Execution time = the timed loop only, after a warm-up run. CPU % and memory = whole process (psutil), so runtimes count.
- Code complexity = lines and tokens of the operation's source (assembly takes more code, especially for division).
- Close other programs, plug in the laptop, and use the same machine for every run.
- Expect surprises: C at -O2 matches assembly, and JIT languages (JavaScript, Java) can beat naive assembly on division because they use faster instructions.

# Usage: python bench.py <add|sub|mul|div|mod> <iterations>
import sys, time

def run(op, n):
    a, b = 1000003, 7
    if op == "add":
        for i in range(n):
            x = a + i; r = x + b
    elif op == "sub":
        for i in range(n):
            x = a + i; r = x - b
    elif op == "mul":
        for i in range(n):
            x = a + i; r = x * b
    elif op == "div":
        for i in range(n):
            x = a + i; r = x // b
    else:
        for i in range(n):
            x = a + i; r = x % b

op, n = sys.argv[1], int(sys.argv[2])
run(op, n // 10 + 1)  # warm-up
t0 = time.perf_counter_ns(); run(op, n); t1 = time.perf_counter_ns()
print(t1 - t0)

// Usage: node bench.js <add|sub|mul|div|mod> <iterations>
let sink = 0;
function run(op, n) {
  const a = 1000003, b = 7;
  if (op === "add") for (let i = 0; i < n; i++) { const x = a + i; sink = x + b; }
  else if (op === "sub") for (let i = 0; i < n; i++) { const x = a + i; sink = x - b; }
  else if (op === "mul") for (let i = 0; i < n; i++) { const x = a + i; sink = x * b; }
  else if (op === "div") for (let i = 0; i < n; i++) { const x = a + i; sink = Math.trunc(x / b); }
  else for (let i = 0; i < n; i++) { const x = a + i; sink = x % b; }
}
const op = process.argv[2], n = parseInt(process.argv[3]);
run(op, Math.floor(n / 10) + 1);
const t0 = process.hrtime.bigint(); run(op, n); const t1 = process.hrtime.bigint();
console.log((t1 - t0).toString());

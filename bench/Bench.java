// Usage: java -cp build Bench <add|sub|mul|div|mod> <iterations>
public class Bench {
    static volatile long sink;
    static void run(String op, long n) {
        long a = 1000003, b = 7;
        switch (op) {
            case "add": for (long i = 0; i < n; i++) { long x = a + i; sink = x + b; } break;
            case "sub": for (long i = 0; i < n; i++) { long x = a + i; sink = x - b; } break;
            case "mul": for (long i = 0; i < n; i++) { long x = a + i; sink = x * b; } break;
            case "div": for (long i = 0; i < n; i++) { long x = a + i; sink = x / b; } break;
            default:    for (long i = 0; i < n; i++) { long x = a + i; sink = x % b; } break;
        }
    }
    public static void main(String[] args) {
        String op = args[0]; long n = Long.parseLong(args[1]);
        run(op, n / 10 + 1);
        long t0 = System.nanoTime(); run(op, n); long t1 = System.nanoTime();
        System.out.println(t1 - t0);
    }
}

/* Usage: bench <asm|c> <add|sub|mul|div|mod> <iterations>   -> prints loop time in ns */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifdef _WIN32
#include <windows.h>
static long long now_ns(void){LARGE_INTEGER f,c;QueryPerformanceFrequency(&f);QueryPerformanceCounter(&c);return (long long)((double)c.QuadPart*1e9/(double)f.QuadPart);}
#else
static long long now_ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000000000LL+t.tv_nsec;}
#endif
volatile long long sink;               /* stops the compiler deleting the loop */
volatile long long A = 1000003, B = 7; /* unknown to the compiler at build time */

#define LOOP_C(EXPR) { long long a=A,b=B; for(long long i=0;i<n;i++){ long long x=a+i,y=b; sink=(EXPR); } }
#define LOOP_ASM2(INS) { long long a=A,b=B; for(long long i=0;i<n;i++){ long long x=a+i,y=b,r; \
    __asm__ volatile(INS " %2, %0" : "=r"(r) : "0"(x), "r"(y)); sink=r; } }
#define LOOP_ASMDIV(RES) { long long a=A,b=B; for(long long i=0;i<n;i++){ long long x=a+i,y=b,q,r; \
    __asm__ volatile("cqto\n\tidivq %3" : "=a"(q), "=&d"(r) : "a"(x), "r"(y) : "cc"); sink=RES; } }

static void run(int useasm, const char *op, long long n) {
    if (useasm) {
        if      (!strcmp(op,"add")) LOOP_ASM2("addq")
        else if (!strcmp(op,"sub")) LOOP_ASM2("subq")
        else if (!strcmp(op,"mul")) LOOP_ASM2("imulq")
        else if (!strcmp(op,"div")) LOOP_ASMDIV(q)
        else                        LOOP_ASMDIV(r)
    } else {
        if      (!strcmp(op,"add")) LOOP_C(x+y)
        else if (!strcmp(op,"sub")) LOOP_C(x-y)
        else if (!strcmp(op,"mul")) LOOP_C(x*y)
        else if (!strcmp(op,"div")) LOOP_C(x/y)
        else                        LOOP_C(x%y)
    }
}
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr,"usage: bench <asm|c> <op> <n>\n"); return 1; }
    int useasm = !strcmp(argv[1],"asm"); long long n = atoll(argv[3]);
    run(useasm, argv[2], n/10 + 1);            /* warm-up */
    long long t0 = now_ns(); run(useasm, argv[2], n); long long t1 = now_ns();
    printf("%lld\n", t1 - t0);
    return 0;
}

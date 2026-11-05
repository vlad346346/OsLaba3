import sys
import time
import csv
import math
import threading

# Аргументи командного рядка: n та режим (0.005 або 1e-6)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
mode = sys.argv[2] if len(sys.argv) > 2 else "0.005"

NT = 2 + (n % 3)        # 3
INC = 200 + 20 * n      # 520
R = 1000
expected = NT * INC     # 1560
cc = (53 * n + 7) % 97  # 79
TOKEN = f"LAB3-{n:02d}-{cc:02d}"

sys.setswitchinterval(float(mode))

def step(val):
    return val + 1

# Вимір накладних витрат таймера
t_diffs = []
for _ in range(1000):
    t0 = time.perf_counter_ns()
    t1 = time.perf_counter_ns()
    t_diffs.append(t1 - t0)
t_diffs.sort()
print(f"Накладні витрати таймера (медіана): {t_diffs[500]} нс")

rows = []
for t_idx in range(R):
    counter = 0
    barrier = threading.Barrier(NT)

    def worker():
        global counter
        barrier.wait()
        for _ in range(INC):
            counter = step(counter)

    threads = [threading.Thread(target=worker) for _ in range(NT)]
    t0 = time.perf_counter_ns()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    dt = time.perf_counter_ns() - t0

    lost = expected - counter
    rows.append([t_idx, expected, counter, lost, dt])

csv_name = f"data/race_none_{mode}_{TOKEN}.csv"
with open(csv_name, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t_idx", "expected", "actual", "lost", "time_ns"])
    writer.writerows(rows)

# Відкидаємо перші 5% (50 повторів) як розігрів
warmup = math.floor(0.05 * R)
clean_rows = rows[warmup:]

lost_vals = sorted([r[3] for r in clean_rows])
time_us = sorted([r[4] / 1000.0 for r in clean_rows])
k = len(clean_rows)

loss_runs_total = sum(1 for r in rows if r[3] > 0)
loss_runs_clean = sum(1 for x in lost_vals if x > 0)

def p_val(arr, p):
    return arr[min(k - 1, int(math.ceil(p / 100.0 * k)) - 1)]

print(f"\n--- Режим: {mode} с (файл: {csv_name}) ---")
print(f"Повторів із втратами (усі 1000): {loss_runs_total} ({loss_runs_total/10:.1f}%)")
print(f"Повторів із втратами (після розігріву, з 950): {loss_runs_clean} ({loss_runs_clean/9.5:.1f}%)")
print(f"Втрати (lost): min={lost_vals[0]}, медіана={lost_vals[k//2]}, середнє={sum(lost_vals)/k:.1f}, p95={p_val(lost_vals, 95)}, p99={p_val(lost_vals, 99)}, max={lost_vals[-1]}")
print(f"Час (мкс):     min={time_us[0]:.1f}, медіана={time_us[k//2]:.1f}, середнє={sum(time_us)/k:.1f}, p95={p_val(time_us, 95):.1f}, p99={p_val(time_us, 99):.1f}, max={time_us[-1]:.1f}")

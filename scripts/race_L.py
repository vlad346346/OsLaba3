import sys, time, csv, math, threading

n = 16
NT, INC, R = 2 + (n % 3), 200 + 20 * n, 1000
expected = NT * INC
TOKEN = f"LAB3-{n:02d}-{(53 * n + 7) % 97:02d}"
sys.setswitchinterval(1e-6)

def step(val):
    return val + 1

rows = []
for t_idx in range(R):
    counter = 0
    barrier = threading.Barrier(NT)
    lock = threading.Lock()

    def worker():
        global counter
        barrier.wait()
        for _ in range(INC):
            with lock:
                counter = step(counter)

    threads = [threading.Thread(target=worker) for _ in range(NT)]
    t0 = time.perf_counter_ns()
    for t in threads: t.start()
    for t in threads: t.join()
    dt = time.perf_counter_ns() - t0
    rows.append([t_idx, expected, counter, expected - counter, dt])

csv_name = f"data/race_L_{TOKEN}.csv"
with open(csv_name, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["t_idx", "expected", "actual", "lost", "time_ns"])
    w.writerows(rows)

clean = rows[math.floor(0.05 * R):]
time_us = sorted([r[4] / 1000.0 for r in clean])
k = len(time_us)
p95 = time_us[int(math.ceil(0.95 * k)) - 1]
p99 = time_us[int(math.ceil(0.99 * k)) - 1]
losses = sum(1 for r in rows if r[3] != 0)
print(f"Версія L ({csv_name}): втрат={losses}/1000 | медіана={time_us[k//2]:.1f} мкс | середнє={sum(time_us)/k:.1f} мкс | p95={p95:.1f} мкс | p99={p99:.1f} мкс")

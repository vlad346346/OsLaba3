import os
import time
import csv
import math

TOKEN = "LAB3-16-79"
BLOCK_SIZES = [512, 4096, 65536, 1048576]
MODES = ['buffered', 'fsync']
FILE_NAME = f"data/test_io_{TOKEN}.bin"

os.makedirs("data", exist_ok=True)

def percentile(data, p):
    idx = int(math.ceil(p / 100.0 * len(data))) - 1
    return data[max(0, min(idx, len(data) - 1))]

print(f"=== Завдання 6: Бенчмарк вводу-виводу (PID = {os.getpid()}) ===")
input("Запусти монітор у другому вікні і натисни Enter для старту бенчмарку...")

print("Режим    | Блок (Б) | Медіана (мкс) | p95 (мкс) | p99 (мкс) | IOPS      | МБ/с")
print("-" * 85)

for block_size in BLOCK_SIZES:
    for mode in MODES:
        iterations = max(100, 10 * 1024 * 1024 // block_size) # Близько 10 МБ даних
        if mode == 'fsync' and block_size < 65536:
            iterations = min(iterations, 200) # fsync на малих блоках дуже повільний
        
        data_block = b'x' * block_size
        times = []
        
        # Відкриваємо файл (O_BINARY потрібен для Windows)
        fd = os.open(FILE_NAME, os.O_CREAT | os.O_WRONLY | os.O_TRUNC | getattr(os, 'O_BINARY', 0))
        
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            os.write(fd, data_block)
            if mode == 'fsync':
                os.fsync(fd)
            t1 = time.perf_counter_ns()
            times.append(t1 - t0)
            
        # Збереження фінального fsync для buffered (як вимагає методичка)
        if mode == 'buffered':
            os.fsync(fd)
        os.close(fd)
        
        # Відкидаємо перші 5% (розігрів)
        skip = math.floor(0.05 * len(times))
        clean_times = sorted(times[skip:])
        
        med = clean_times[len(clean_times)//2] / 1000.0
        p95 = percentile(clean_times, 95) / 1000.0
        p99 = percentile(clean_times, 99) / 1000.0
        
        iops = 1_000_000.0 / med if med > 0 else 0
        mb_s = (iops * block_size) / (1024 * 1024)
        
        print(f"{mode:<8} | {block_size:<8} | {med:<13.1f} | {p95:<9.1f} | {p99:<9.1f} | {iops:<9.1f} | {mb_s:.1f}")
        
        # Збереження CSV
        with open(f"data/io_{mode}_{block_size}_{TOKEN}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["t_ns"])
            for t in times: writer.writerow([t])

# === Перевірка Page Cache ===
print("\n=== Перевірка Page Cache (Читання файлу двічі) ===")
for run in [1, 2]:
    fd = os.open(FILE_NAME, os.O_RDONLY | getattr(os, 'O_BINARY', 0))
    t0 = time.perf_counter()
    while True:
        b = os.read(fd, 65536)
        if not b: break
    t1 = time.perf_counter()
    os.close(fd)
    print(f"Читання {run}: {(t1 - t0)*1000:.2f} мс")
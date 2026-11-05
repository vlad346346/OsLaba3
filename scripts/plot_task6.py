import csv
import matplotlib.pyplot as plt
import os
import math

TOKEN = "LAB3-16-79"
BLOCK_SIZES = [512, 4096, 65536, 1048576]
MODES = ['buffered', 'fsync']

# 1. Графік write_bytes (із монітора)
monitor_file = f"data/monitor_res_{TOKEN}.csv"
if os.path.exists(monitor_file):
    times, wb = [], []
    with open(monitor_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["write_bytes"] != "NA":
                times.append(float(row["ts_ms"]) / 1000.0)
                wb.append(float(row["write_bytes"]) / (1024*1024))
    if times:
        plt.figure(figsize=(10, 5))
        plt.plot(times, wb, label='write_bytes', color='purple', linewidth=2)
        plt.xlabel('Час (с)')
        plt.ylabel('МБ записано')
        plt.title('Накопичений запис даних (write_bytes) у часі [LAB3-16-79]')
        plt.grid(True, linestyle='--')
        plt.tight_layout()
        plt.savefig('data/task6_write_bytes_chart.png')
        print("Згенеровано: data/task6_write_bytes_chart.png")

# 2. Графіки Затримки і Пропускної здатності
lat_buf, lat_fsync = [], []
mb_buf, mb_fsync = [], []

def get_stats(mode, block):
    file_path = f"data/io_{mode}_{block}_{TOKEN}.csv"
    times = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                times.append(float(row[0]))
    if times:
        skip = math.floor(0.05 * len(times))
        clean = sorted(times[skip:])
        med = clean[len(clean)//2] / 1000.0
        iops = 1_000_000.0 / med if med > 0 else 0
        mb = (iops * block) / (1024*1024)
        return med, mb
    return 0, 0

for b in BLOCK_SIZES:
    m_buf, tb_buf = get_stats('buffered', b)
    m_fsync, tb_fsync = get_stats('fsync', b)
    
    lat_buf.append(m_buf)
    lat_fsync.append(m_fsync)
    mb_buf.append(tb_buf)
    mb_fsync.append(tb_fsync)

# Затримка
plt.figure(figsize=(8, 5))
plt.plot(BLOCK_SIZES, lat_buf, marker='o', linewidth=2, label='buffered')
plt.plot(BLOCK_SIZES, lat_fsync, marker='s', linewidth=2, color='#e8713a', label='fsync')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Розмір блоку (Байт)')
plt.ylabel('Затримка (мкс, log)')
plt.title('Затримка від розміру блоку [LAB3-16-79]')
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig('data/task6_latency.png')
print("Згенеровано: data/task6_latency.png")

# Пропускна здатність
plt.figure(figsize=(8, 5))
plt.plot(BLOCK_SIZES, mb_buf, marker='o', linewidth=2, label='buffered')
plt.plot(BLOCK_SIZES, mb_fsync, marker='s', linewidth=2, color='#e8713a', label='fsync')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Розмір блоку (Байт)')
plt.ylabel('Пропускна здатність (МБ/с, log)')
plt.title('Пропускна здатність від розміру блоку [LAB3-16-79]')
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig('data/task6_throughput.png')
print("Згенеровано: data/task6_throughput.png")
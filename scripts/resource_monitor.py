import sys
import time
import csv
import os
import psutil

if len(sys.argv) < 3:
    print("Використання: python scripts\\resource_monitor.py <PID> <delta_sec> [points]")
    sys.exit(1)

target_pid = int(sys.argv[1])
delta = float(sys.argv[2])
points = int(sys.argv[3]) if len(sys.argv) > 3 else 600
TOKEN = "LAB3-16-79"

csv_name = f"data/monitor_res_{TOKEN}.csv"
os.makedirs("data", exist_ok=True)

print(f"Моніторинг PID {target_pid} з інтервалом {delta} с (всього точок: {points})...")

try:
    p = psutil.Process(target_pid)
except psutil.NoSuchProcess:
    print(f"Процес з PID {target_pid} не знайдено.")
    sys.exit(1)

with open(csv_name, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["t_idx", "ts_ms", "rss_kb", "vsz_kb", "threads", "page_faults", "read_bytes", "write_bytes"])
    
    start_time = time.time_ns()
    
    for idx in range(points):
        ts_ms = (time.time_ns() - start_time) // 1_000_000
        
        try:
            with p.oneshot():
                mem = p.memory_info()
                io = p.io_counters()
                
                rss_kb = mem.rss // 1024
                vsz_kb = mem.vms // 1024
                threads = p.num_threads()
                page_faults = getattr(mem, 'num_page_faults', 'NA')
                read_bytes = io.read_bytes
                write_bytes = io.write_bytes
                
            writer.writerow([idx, ts_ms, rss_kb, vsz_kb, threads, page_faults, read_bytes, write_bytes])
            f.flush() # Примусово скидаємо у файл
        except Exception:
            print(f"Процес {target_pid} завершився.")
            break
            
        time.sleep(delta)

print(f"Моніторинг завершено. Дані збережено у {csv_name}")
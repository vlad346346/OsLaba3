import sys
import time
import csv
import mmap
import ctypes
import os

n = 16
MEM_MB = 64 + 8 * n  # 192 МБ
MEM_BYTES = MEM_MB * 1024 * 1024
TOKEN = "LAB3-16-79"

print(f"=== Фаза A: Старт (PID = {os.getpid()}) ===")
print(f"Розмір сторінки ОС (PAGESIZE) = {mmap.PAGESIZE} байт")
input("Натисніть Enter для переходу до фази B (виділення mmap)...")

print(f"\n=== Фаза Б: Виділення {MEM_MB} МБ через mmap ===")
# Створюємо анонімне відображення в пам'яті
m = mmap.mmap(-1, MEM_BYTES, access=mmap.ACCESS_WRITE)

# Отримуємо віртуальну адресу початку відображення (длявідповіді на п. 5.4.1)
try:
    if sys.platform == "win32":
        # У Windows отримуємо вказівник через ctypes
        addr = ctypes.addressof(ctypes.c_char.from_buffer(m))
    else:
        addr = "недоступно"
    print(f"Адреса початку відображення mmap: hex(0x{addr:X})" if isinstance(addr, int) else f"Адреса: {addr}")
except Exception as e:
    print(f"Адреса mmap: (не вдалося отримати напряму: {e})")

input("Зніміть показники VSZ/RSS (Фаза B) та натисніть Enter для першого проходу (Фаза C)...")

print(f"\n=== Фаза C: Перший прохід (запис 1 байта в кожну сторінку) ===")
page_size = mmap.PAGESIZE
num_pages = MEM_BYTES // page_size

pass1_times = []
t_total_start = time.perf_counter_ns()

for i in range(num_pages):
    off = i * page_size
    t0 = time.perf_counter_ns()
    # Записуємо 1 байт у початок кожної сторінки
    m[off] = 1
    dt = time.perf_counter_ns() - t0
    pass1_times.append((i, dt))

print(f"Перший прохід завершено за {(time.perf_counter_ns() - t_total_start) / 1e6:.2f} мс.")
input("Зніміть показники RSS та Page Faults (Фаза C) та натисніть Enter для другого проходу (Фаза D)...")

print(f"\n=== Фаза D: Другий прохід (повторний запис) ===")
pass2_times = []
t_total_start = time.perf_counter_ns()

for i in range(num_pages):
    off = i * page_size
    t0 = time.perf_counter_ns()
    m[off] = 1
    dt = time.perf_counter_ns() - t0
    pass2_times.append(dt)

print(f"Другий прохід завершено за {(time.perf_counter_ns() - t_total_start) / 1e6:.2f} мс.")

# Зберігаємо часи до CSV
os.makedirs("data", exist_ok=True)
csv_name = f"data/pages_{TOKEN}.csv"
with open(csv_name, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t_idx", "pass1_ns", "pass2_ns"])
    for i, (idx, t1) in enumerate(pass1_times):
        w.writerow([idx, t1, pass2_times[i]])

print(f"Дані дотиків збережено у {csv_name}")
input("Зніміть фінальні показники (Фаза D) та натисніть Enter для завершення програми...")
m.close()
print("Відомокремлену пам'ять звільнено.")

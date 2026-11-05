import threading
import time
import csv
import os

TOKEN = "LAB3-16-79"
B = 4
P = 1
C = 1
ITEMS = 2000

class BoundedBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.mutex = threading.Lock()
        self.not_full = threading.Condition(self.mutex)
        self.not_empty = threading.Condition(self.mutex)
        self.waits_put = 0
        self.waits_get = 0

    def put(self, item):
        with self.not_full:
            while len(self.buffer) >= self.capacity:
                self.waits_put += 1
                self.not_full.wait()
            self.buffer.append(item)
            self.not_empty.notify()

    def get(self):
        with self.not_empty:
            while len(self.buffer) == 0:
                self.waits_get += 1
                self.not_empty.wait()
            item = self.buffer.pop(0)
            self.not_full.notify()
            return item

def run_experiment(mode, run_id):
    bb = BoundedBuffer(B)
    delays = []
    received = []
    
    def producer():
        for i in range(ITEMS):
            if mode == 'c': time.sleep(0.005)
            t0 = time.perf_counter_ns()
            bb.put((i, t0))
        bb.put(None) # STOP marker

    def consumer():
        while True:
            if mode == 'b': time.sleep(0.001)
            item = bb.get()
            if item is None: break
            val, t0 = item
            dt = time.perf_counter_ns() - t0
            delays.append(dt)
            received.append(val)

    p_thread = threading.Thread(target=producer)
    c_thread = threading.Thread(target=consumer)
    
    t_start = time.time()
    p_thread.start()
    c_thread.start()
    p_thread.join()
    c_thread.join()
    t_end = time.time()
    
    # Збереження затримок у CSV
    os.makedirs("data", exist_ok=True)
    with open(f"data/buffer_{mode}_run{run_id}_{TOKEN}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item_idx", "delay_ns"])
        for idx, d in enumerate(delays):
            writer.writerow([idx, d])
            
    sum_val = sum(received)
    expected_sum = sum(range(ITEMS))
    unique = len(set(received))
    
    return {
        'mode': mode, 'run': run_id,
        'received': len(received),
        'sum_ok': "Так" if sum_val == expected_sum else "Ні",
        'unique': "Так" if unique == ITEMS else "Ні",
        'waits_put': bb.waits_put,
        'waits_get': bb.waits_get,
        'time_s': t_end - t_start
    }

if __name__ == "__main__":
    print("=== Запуск Завдання 3 (9 запусків) ===")
    results = []
    for mode in ['a', 'b', 'c']:
        for run_id in range(1, 4):
            print(f"Виконується режим '{mode}', запуск {run_id}...")
            res = run_experiment(mode, run_id)
            results.append(res)
            
    print("\n=== Готова таблиця 9 запусків для звіту ===")
    print("Режим | Запуск | Отримано | Сума ОК | Унікальних | waits_put | waits_get | Час (с)")
    print("-" * 85)
    for r in results:
        print(f"  {r['mode']}   |   {r['run']}    |   {r['received']}   |   {r['sum_ok']}   |    {r['unique']}     |   {r['waits_put']:<7} |   {r['waits_get']:<7} | {r['time_s']:.2f}")
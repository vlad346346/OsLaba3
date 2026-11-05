import sys
import time
import threading

n = 16
B = 3 + (n % 5)          # 4
P = 1 + (n % 2)          # 1
C = 3                    # За методичкою для цього досліду всі використовують C = 3
ITEMS = 200
sys.setswitchinterval(1e-6) # Посилений режим перемикання

class BuggyBuffer:
    def __init__(self, capacity):
        self.B = capacity
        self.buf = [None] * capacity
        self.inp = 0
        self.out = 0
        self.count = 0
        self.M = threading.Lock()
        self.not_full = threading.Condition(self.M)
        self.not_empty = threading.Condition(self.M)

    def put(self, item):
        with self.M:
            while self.count == self.B:
                self.not_full.wait()
            self.buf[self.inp] = item
            self.inp = (self.inp + 1) % self.B
            self.count += 1
            self.not_empty.notify_all() # Будимо всіх, як вимагає умова досліду

    def get(self):
        with self.M:
            # ПОМИЛКОВА ЗАМІНА while на if!
            if self.count == 0:
                self.not_empty.wait()
            item = self.buf[self.out]
            self.out = (self.out + 1) % self.B
            self.count -= 1
            self.not_full.notify()
            return item

bb = BuggyBuffer(B)
received = []
lock = threading.Lock()

def producer():
    for i in range(ITEMS):
        bb.put(i)

def consumer(c_id):
    while True:
        try:
            item = bb.get()
            if item is None:
                break
            with lock:
                received.append(item)
        except Exception as e:
            print(f"Споживач {c_id} зловив виняток: {e}")
            break

producers = [threading.Thread(target=producer) for _ in range(P)]
consumers = [threading.Thread(target=consumer, args=(i,)) for i in range(C)]

for t in producers + consumers: t.start()
for t in producers: t.join()

for _ in range(C):
    bb.put(None)

for t in consumers: t.join()

print(f"Отримано елементів: {len(received)} з {ITEMS * P} очікуваних. Унікальних: {len(set(received))}")

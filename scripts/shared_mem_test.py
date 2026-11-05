import multiprocessing
from multiprocessing import shared_memory
import time
import psutil
import sys

TOKEN = "LAB3-16-79"

def child_process(shm_name):
    # Підключаємося до існуючої спільної пам'яті
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    
    # Записуємо токен
    data = TOKEN.encode('utf-8')
    existing_shm.buf[:len(data)] = data
    existing_shm.close()
    
    # Спимо зовсім трохи, щоб батько встиг заміряти наш RSS
    time.sleep(0.1)

if __name__ == '__main__':
    # Обов'язково для Windows (spawn)
    multiprocessing.freeze_support()
    
    print("=== Завдання 5: Спільна пам'ять та 5 запусків spawn ===")
    
    # Створюємо спільну пам'ять (наприклад, 96 МБ)
    shm_size = 96 * 1024 * 1024
    shm = shared_memory.SharedMemory(create=True, size=shm_size)
    print(f"Створено блок спільної пам'яті: ім'я = {shm.name}, розмір = 96.0 МБ")

    results = []
    
    for i in range(1, 6):
        t_start = time.perf_counter()
        
        p = multiprocessing.Process(target=child_process, args=(shm.name,))
        p.start()
        
        # Ловимо RSS нащадка
        child_rss = "NA"
        try:
            time.sleep(0.05) # Чекаємо, поки процес ініціалізується
            proc = psutil.Process(p.pid)
            child_rss = proc.memory_info().rss / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        p.join()
        t_end = time.perf_counter()
        
        # Читаємо, що записав нащадок
        data = bytes(shm.buf[:len(TOKEN)]).decode('utf-8')
        
        results.append({
            'run': i,
            'time_ms': (t_end - t_start) * 1000,
            'rss_kb': child_rss,
            'data': data
        })
        
        # Очищаємо буфер для наступного проходу
        shm.buf[:len(TOKEN)] = b'\x00' * len(TOKEN)

    shm.close()
    shm.unlink()
    print("Блок спільної пам'яті закрито і видалено.\n")
    
    print("=== Таблиця 5 запусків spawn (для звіту) ===")
    print("Запуск | Час виконання (мс) | Стартовий RSS нащадка (КБ) | Прочитано з SHM")
    print("-" * 75)
    for r in results:
        rss_str = f"{r['rss_kb']:.1f}" if isinstance(r['rss_kb'], float) else r['rss_kb']
        print(f"  {r['run']}    | {r['time_ms']:<18.2f} | {rss_str:<26} | '{r['data']}'")
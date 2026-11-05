import csv
import matplotlib.pyplot as plt
import os
import math

TOKEN = "LAB3-16-79"

# 1. Графік RSS та VSZ у часі
monitor_file = f"data/monitor_res_{TOKEN}.csv"
if os.path.exists(monitor_file):
    times, rss, vsz = [], [], []
    with open(monitor_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["rss_kb"] != "NA" and row["vsz_kb"] != "NA":
                times.append(float(row["ts_ms"]) / 1000.0)
                rss.append(float(row["rss_kb"]) / 1024.0)
                vsz.append(float(row["vsz_kb"]) / 1024.0)
    
    if times:
        plt.figure(figsize=(10, 5))
        plt.plot(times, vsz, label='VSZ (Committed)', linewidth=2, color='#4fa1d8')
        plt.plot(times, rss, label='RSS (WorkingSet)', linewidth=2, color='#e8713a')
        plt.xlabel('Час від початку серії (с)')
        plt.ylabel('МБ')
        plt.title(f'Віртуальний і резидентний обсяг у часі [LAB3-16-79]')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('data/task4_rss_vsz.png', dpi=300)
        print("Згенеровано графік RSS: data/task4_rss_vsz.png")
else:
    print("Файл моніторингу не знайдено.")

# 2. Графік Pass1 vs Pass2 (з відкиданням 5% розігріву)
pages_file = f"data/pages_{TOKEN}.csv"
if os.path.exists(pages_file):
    pass1, pass2 = [], []
    with open(pages_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader) # Пропускаємо заголовок
        for row in reader:
            if len(row) >= 3:
                pass1.append(float(row[1]))
                pass2.append(float(row[2]))
    
    if pass1 and pass2:
        # Відкидаємо перші 5% (розігрів)
        skip = math.floor(0.05 * len(pass1))
        pass1_clean = pass1[skip:]
        pass2_clean = pass2[skip:]
        
        plt.figure(figsize=(8, 6))
        plt.boxplot([pass1_clean, pass2_clean], labels=['pass1 (перший дотик)', 'pass2 (повторний)'])
        plt.yscale('log')
        plt.ylabel('Час запису (нс, логарифмічна шкала)')
        plt.title('Час першого та повторного дотику до сторінок [LAB3-16-79]')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig('data/task4_pass_boxplot.png', dpi=300)
        print("Згенеровано графік Pass1/Pass2: data/task4_pass_boxplot.png")
else:
    print("Файл pages.csv не знайдено.")
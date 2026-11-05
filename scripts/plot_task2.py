import csv, math
import matplotlib.pyplot as plt

TOKEN = "LAB3-16-79"
warmup = 50  # 5% від 1000

def read_col(fname, col_idx, scale=1.0):
    with open(f"data/{fname}", "r") as f:
        r = list(csv.reader(f))[1:]
    vals = [float(row[col_idx]) * scale for row in r[warmup:]]
    vals_sorted = sorted(vals)
    k = len(vals_sorted)
    med = vals_sorted[k // 2]
    p95 = vals_sorted[int(math.ceil(0.95 * k)) - 1]
    return vals, med, p95

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

# 1. Гістограма lost для 1e-6
lost_vals, l_med, l_p95 = read_col(f"race_none_1e-6_{TOKEN}.csv", 3)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
ax.hist(lost_vals, bins=25, color="#4C72B0", edgecolor="black", alpha=0.85)
ax.axvline(l_med, color="green", linewidth=2, label=f"Медіана = {l_med:.0f}")
ax.axvline(l_p95, color="red", linestyle="--", linewidth=2, label=f"p95 = {l_p95:.0f}")
ax.set_title(f"Гістограма кількості втрачених оновлень (1e-6 с, N=950) [{TOKEN}]")
ax.set_xlabel("Кількість втрачених оновлень (lost), од.")
ax.set_ylabel("Кількість повторів, од.")
ax.legend()
ax.grid(axis="y", linestyle=":", alpha=0.6)
fig.tight_layout()
fig.savefig(f"screenshots/task2_hist_lost_{TOKEN}.png")
plt.close(fig)

# 2. Діаграма медіан часу з p95 як вусами
files = [
    ("none (0.005s)", f"race_none_0.005_{TOKEN}.csv"),
    ("none (1e-6s)",  f"race_none_1e-6_{TOKEN}.csv"),
    ("L (Lock)",      f"race_L_{TOKEN}.csv"),
    ("S (Semaphore)", f"race_S_{TOKEN}.csv"),
    ("G (Local)",     f"race_G_{TOKEN}.csv"),
]
labels, meds, err_up = [], [], []
for lbl, fn in files:
    _, med, p95 = read_col(fn, 4, scale=1/1000.0)
    labels.append(lbl)
    meds.append(med)
    err_up.append(max(0, p95 - med))

fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
bars = ax.bar(labels, meds, yerr=[[0]*len(meds), err_up], capsize=6,
              color=["#8172B2", "#C44E52", "#4C72B0", "#DD8452", "#55A868"],
              edgecolor="black", alpha=0.88, label="Медіана часу (вуса = p95)")
ax.set_yscale("log")
ax.set_title(f"Порівняння часу виконання версій синхронізації (лог. шкала) [{TOKEN}]")
ax.set_xlabel("Версія програми")
ax.set_ylabel("Час одного повтору, мкс (log scale)")
for bar, med in zip(bars, meds):
    ax.text(bar.get_x() + bar.get_width()/2, med * 1.08, f"{med:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.legend()
ax.grid(axis="y", linestyle=":", alpha=0.6)
fig.tight_layout()
fig.savefig(f"screenshots/task2_sync_times_{TOKEN}.png")
plt.close(fig)
print("Графіки збережено у папку screenshots!")

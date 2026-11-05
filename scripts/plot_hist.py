import csv, math
import matplotlib.pyplot as plt

TOKEN = "LAB3-16-79"
warmup = 50  # відкидаємо перші 5% (50 із 1000 повторів)

with open(f"data/race_none_1e-6_{TOKEN}.csv", "r") as f:
    rows = list(csv.reader(f))[1:]

lost_vals = [int(r[3]) for r in rows[warmup:]]
lost_sorted = sorted(lost_vals)
k = len(lost_sorted)
med_lost = lost_sorted[k // 2]
mean_lost = sum(lost_sorted) / k
p95_lost = lost_sorted[int(math.ceil(0.95 * k)) - 1]

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
ax.hist(lost_vals, bins=25, color="#4C72B0", edgecolor="black", alpha=0.85)
ax.axvline(med_lost, color="green", linewidth=2, label=f"Медіана = {med_lost}")
ax.axvline(mean_lost, color="orange", linestyle="-.", linewidth=2, label=f"Середнє = {mean_lost:.1f}")
ax.axvline(p95_lost, color="red", linestyle="--", linewidth=2, label=f"p95 = {p95_lost}")

ax.set_title(f"Гістограма втрачених оновлень (lost) у серії 1e-6 с [{TOKEN}]")
ax.set_xlabel("Кількість втрачених оновлень (lost), од.")
ax.set_ylabel("Кількість повторів, од.")
ax.legend()
ax.grid(axis="y", linestyle=":", alpha=0.6)
fig.tight_layout()

out_path = f"screenshots/hist_lost_1e-6_{TOKEN}.png"
fig.savefig(out_path)
print(f"Гістограму збережено у: {out_path}")

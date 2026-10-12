# 1. Inisialisasi Library dan Konfigurasi
import numpy as np, pandas as pd, matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "sans-serif", "font.size": 9.5, "figure.facecolor": "white",
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300, "savefig.bbox": "tight"})
J = lambda t: print(f"\n{'=' * 62}\n{t}\n{'=' * 62}")  # mencetak judul bagian output

df = pd.read_excel("3TIF_07_StudentPerformance.xlsx", sheet_name="Data")  # membaca data
H, S, Y = "Hours Studied", "Sleep Hours", "Performance Index"
v = df[[H, S, Y]]

# 2. Pembacaan Data dan Pemeriksaan Kualitas Data
J("1. KUALITAS DATA")
print("Jumlah baris, kolom   :", df.shape)
print("Baris duplikat        :", df.duplicated().sum())
print("Nilai kosong per kolom:", df.isna().sum(), sep="\n")
df["Kategori"] = pd.cut(df[H], [0, 3, 6, 9], labels=["Rendah (1-3 jam)", "Sedang (4-6 jam)", "Tinggi (7-9 jam)"])

# 3. Statistika Deskriptif dan Batas Outlier (Aturan IQR)
J("2. STATISTIK DESKRIPTIF DAN OUTLIER (ATURAN IQR)")
t = pd.concat([v.describe().T, v.agg(["sem", "median", "var", "skew", "kurt"]).T], axis=1)
t["modus"] = v.mode().iloc[0]
t["range"] = t["max"] - t["min"]
t["IQR"] = t["75%"] - t["25%"]
t["batas_bawah"] = t["25%"] - 1.5 * t["IQR"]
t["batas_atas"] = t["75%"] + 1.5 * t["IQR"]
t["n_outlier"] = ((v < t["batas_bawah"]) | (v > t["batas_atas"])).sum()
print(t.round(3).T.to_string(float_format=lambda x: f"{x:,.0f}" if x == int(x) else f"{x:.3f}"))

# 4. Distribusi Frekuensi, Peluang Empiris, dan Peluang Bersyarat
for c, k in [(H, 7), (S, 8)]:
    J(f"3. FREKUENSI DAN PELUANG EMPIRIS: {c.upper()}")
    f = pd.crosstab(df[c], "Frekuensi")
    f["Peluang"] = (f["Frekuensi"] / f["Frekuensi"].sum()).round(4)
    f["Persentase (%)"] = (f["Peluang"] * 100).round(2)
    f.loc["Total"] = f.sum()
    f["Frekuensi"] = f["Frekuensi"].astype(int)
    print(f.rename_axis(None, axis=1), f"\nP({c} >= {k}) = {(df[c] >= k).mean():.4f}")
    print(f"\n--- Ringkasan Performance Index menurut {c} ---")
    print(df.groupby(c)[Y].describe()[["count", "mean", "50%", "25%", "75%", "min", "max"]].round(2))

J("4. PELUANG BERSYARAT PERFORMANCE INDEX >= 70 PER KATEGORI JAM BELAJAR")
g = (df[Y] >= 70).groupby(df["Kategori"], observed=True).agg(["size", "mean"])
print(g.rename(columns={"size": "Jumlah Siswa", "mean": "P(Y>=70 | kategori)"}).round(4))

# 5. Visualisasi Data (Diagram Batang, Boxplot, dan Distribusi)
J("5. GRAFIK (disimpan sebagai file PNG)")

# Grafik 1: diagram batang peluang bersyarat
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.bar_label(ax.bar(g.index, g["mean"], width=0.55, color=["#90b8d8", "#468faf", "#2a6f97"]), fmt="%.4f", padding=2)
ax.set(ylim=(0, 0.5), xlabel="Kategori jam belajar", ylabel="P(Y ≥ 70 | kategori)")
fig.savefig("grafik1_peluang_kategori.png")

# Grafik 2: boxplot Performance Index menurut jam belajar dan jam tidur
fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
for ax, c, n in zip(axs, (H, S), ("Jam Belajar", "Jam Tidur")):
    k = np.sort(df[c].unique())
    ax.boxplot([df.loc[df[c] == i, Y] for i in k], tick_labels=k, patch_artist=True,
               boxprops={"facecolor": "white"}, medianprops={"color": "gray"})
    ax.set(title=f"Performance Index menurut {n}", xlabel=n, ylabel=Y)
fig.savefig("grafik2_boxplot.png")

# Grafik 3: distribusi jam belajar, jam tidur, dan Performance Index
fig, axs = plt.subplots(1, 3, figsize=(12, 3.4))
for ax, c, col, n in zip(axs, (H, S, Y), ("#2a6f97", "#468faf", "#8a5a44"), 
                         ("Jam Belajar (X1)", "Jam Tidur (X2)", "Performance Index (Y)")):
    if c == Y: ax.hist(df[c], bins=20, color=col, edgecolor="white")
    else:
        f = df[c].value_counts().sort_index()
        ax.bar(f.index, f, color=col)
        ax.set_xticks(f.index)
    ax.set(title=n, xlabel="Poin" if c == Y else "Jam per hari", ylabel="Frekuensi" if c == H else "")
fig.savefig("grafik3_distribusi.png")
print("grafik1_peluang_kategori.png, grafik2_boxplot.png, grafik3_distribusi.png")
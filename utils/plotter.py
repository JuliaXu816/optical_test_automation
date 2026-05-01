import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def plot_osnr_sweep(launch_powers: list, osnr_values: list, threshold: float, save_path: str = "reports/osnr_sweep.png"):
    os.makedirs("reports", exist_ok=True)
    colors = ["green" if o >= threshold else "red" for o in osnr_values]
    plt.figure(figsize=(10, 6))
    plt.plot(launch_powers, osnr_values, "b-o", linewidth=2, markersize=8)
    plt.axhline(y=threshold, color="red", linestyle="--", linewidth=1.5, label=f"Threshold {threshold} dB")
    plt.scatter(launch_powers, osnr_values, c=colors, s=100, zorder=5)
    plt.xlabel("Launch Power (dBm)", fontsize=12)
    plt.ylabel("OSNR (dB)", fontsize=12)
    plt.title("OSNR vs Launch Power Sweep", fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"[PLOT] Saved to {save_path}")

def plot_ber_sweep(launch_powers: list, ber_values: list, threshold: float, save_path: str = "reports/ber_sweep.png"):
    os.makedirs("reports", exist_ok=True)
    colors = ["green" if b <= threshold else "red" for b in ber_values]
    plt.figure(figsize=(10, 6))
    plt.semilogy(launch_powers, ber_values, "b-o", linewidth=2, markersize=8)
    plt.axhline(y=threshold, color="red", linestyle="--", linewidth=1.5, label=f"Threshold {threshold:.2e}")
    plt.scatter(launch_powers, ber_values, c=colors, s=100, zorder=5)
    plt.xlabel("Launch Power (dBm)", fontsize=12)
    plt.ylabel("BER (log scale)", fontsize=12)
    plt.title("BER vs Launch Power Sweep", fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"[PLOT] Saved to {save_path}")
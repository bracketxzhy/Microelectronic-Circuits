from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


VPP = 14.0
FREQUENCY_HZ = 1_000.0
DIODE_DROP_V = 0.7
BIAS_V = 3.0
CLIP_LEVEL_V = BIAS_V + DIODE_DROP_V


def clipped_output(vin: np.ndarray) -> np.ndarray:
    """Constant-voltage-drop model for the biased positive limiter in Figure 1."""
    return np.minimum(vin, CLIP_LEVEL_V)


def save_transfer_plot(output_dir: Path) -> Path:
    vin = np.linspace(-8.0, 8.0, 2001)
    vout = clipped_output(vin)

    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    ax.plot(vin, vout, color="#0b57d0", linewidth=2.5, label=r"$V_{out}$")
    ax.plot(vin, vin, "--", color="#9aa0a6", linewidth=1.5, label=r"$V_{out}=V_{in}$")
    ax.axhline(CLIP_LEVEL_V, color="#d93025", linestyle="--", linewidth=1.5)
    ax.axvline(CLIP_LEVEL_V, color="#d93025", linestyle="--", linewidth=1.5)

    ax.annotate(
        "diode turns on\n$V_{in}\\approx 3.7\\,\\mathrm{V}$",
        xy=(CLIP_LEVEL_V, CLIP_LEVEL_V),
        xytext=(4.6, 1.7),
        arrowprops={"arrowstyle": "->", "linewidth": 1.2, "color": "#d93025"},
        fontsize=11,
        color="#d93025",
    )
    ax.text(
        -7.5,
        6.8,
        r"$V_{out}=\min(V_{in},\,3.7\ \mathrm{V})$",
        fontsize=12,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#c7c7c7"},
    )

    ax.set_title("Action 1.1 Transfer Characteristic (Constant-Voltage-Drop Model)", fontsize=14)
    ax.set_xlabel(r"$V_{in}$ (V)", fontsize=12)
    ax.set_ylabel(r"$V_{out}$ (V)", fontsize=12)
    ax.set_xlim(-8.0, 8.0)
    ax.set_ylim(-8.0, 8.0)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", frameon=True)

    output_path = output_dir / "action1_1_transfer_characteristic.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def save_time_domain_plot(output_dir: Path) -> Path:
    amplitude = VPP / 2.0
    t = np.linspace(0.0, 2.5 / FREQUENCY_HZ, 2500)
    vin = amplitude * np.sin(2.0 * np.pi * FREQUENCY_HZ * t)
    vout = clipped_output(vin)

    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    ax.plot(t * 1e3, vin, color="#1a73e8", linewidth=2.2, label=r"$V_{in}(t)$")
    ax.plot(t * 1e3, vout, color="#d93025", linewidth=2.2, label=r"$V_{out}(t)$")
    ax.axhline(CLIP_LEVEL_V, color="#d93025", linestyle="--", linewidth=1.4, alpha=0.9)

    ax.annotate(
        "positive peaks clipped at 3.7 V",
        xy=(0.31, CLIP_LEVEL_V),
        xytext=(0.76, 6.95),
        arrowprops={"arrowstyle": "->", "linewidth": 1.2, "color": "#d93025"},
        fontsize=11,
        color="#d93025",
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.9},
    )
    ax.text(
        1.78,
        -7.15,
        "Input: 14 Vpp, 1 kHz sine\nModel: 3 V bias + 0.7 V diode drop",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#c7c7c7"},
    )

    ax.set_title("Action 1.1 Time-Domain Waveforms", fontsize=14)
    ax.set_xlabel("Time (ms)", fontsize=12)
    ax.set_ylabel("Voltage (V)", fontsize=12)
    ax.set_xlim(0.0, t[-1] * 1e3)
    ax.set_ylim(-8.0, 8.0)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", frameon=True)

    output_path = output_dir / "action1_1_time_domain.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    transfer_path = save_transfer_plot(output_dir)
    time_path = save_time_domain_plot(output_dir)

    print("Generated files:")
    print(transfer_path)
    print(time_path)


if __name__ == "__main__":
    main()

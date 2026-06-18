from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .analysis import spectrum


def save_spectrum(samples, fs, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    freq, spec = spectrum(samples, fs)
    spec = spec / (spec.max() + 1e-12)

    plt.figure()
    plt.plot(freq, spec)
    plt.xlim(0, 5000)
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Amplitud normalizada")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def build_animation(result, fps=60):
    if result.frames is None:
        raise ValueError("La simulación no guardó frames")

    y_max = np.max(np.abs(result.frames)) + 1e-12

    fig, ax = plt.subplots()
    line, = ax.plot(result.x, result.frames[0])

    ax.set_xlim(result.x[0], result.x[-1])
    ax.set_ylim(-y_max, y_max)
    ax.set_xlabel("x")
    ax.set_ylabel("u(x,t)")

    def update(k):
        line.set_ydata(result.frames[k])
        return line,

    ani = FuncAnimation(
        fig,
        update,
        frames=len(result.frames),
        interval=1000 / fps,
        blit=False,
    )

    return fig, ani


def save_animation_html(result, path, fps=60):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ani = build_animation(result, fps)
    path.write_text(ani.to_jshtml(fps=fps), encoding="utf-8")
    plt.close(fig)


def show_animation(result, fps=60):
    _, ani = build_animation(result, fps)
    plt.show(block=True)
    return ani
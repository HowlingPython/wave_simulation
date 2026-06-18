from dataclasses import dataclass
import numpy as np

from .config import Params


@dataclass
class SimulationResult:
    samples: np.ndarray
    x: np.ndarray
    frames: np.ndarray | None
    c: float
    dx: float
    dt: float
    r: float
    N: int
    x_pluck: float
    x_pickup: float


def triangular_pluck(x, xp, L, amplitude):
    u = np.where(
        x <= xp,
        amplitude * x / xp,
        amplitude * (L - x) / (L - xp),
    )
    u[0] = 0.0
    u[-1] = 0.0
    return u


def simulate(p: Params, keep_frames=False, fps=60):
    dt = 1 / p.fs
    c = 2 * p.L * p.f1
    N = max(int(np.floor(p.fs / (2 * p.f1))), 4)
    dx = p.L / N
    r = c * dt / dx

    if r > 1:
        raise ValueError(f"Condición CFL violada: r={r:.6f}")

    x = np.linspace(0, p.L, N + 1)

    i_pluck = max(1, min(N - 1, int(round(p.pluck_pos * N))))
    i_pickup = max(1, min(N - 1, int(round(p.pickup_pos * N))))

    xp = x[i_pluck]
    x_pickup = x[i_pickup]

    u_prev = triangular_pluck(x, xp, p.L, p.amplitude)
    u_curr = u_prev.copy()

    D0 = u_prev[2:] - 2 * u_prev[1:-1] + u_prev[:-2]
    u_curr[1:-1] = u_prev[1:-1] + 0.5 * r**2 * D0
    u_curr[0] = 0.0
    u_curr[-1] = 0.0

    n_steps = max(2, int(p.duration * p.fs))
    samples = np.zeros(n_steps)
    samples[0] = u_prev[i_pickup]
    samples[1] = u_curr[i_pickup]

    frame_every = max(1, p.fs // fps)
    frames = [u_prev.copy()] if keep_frames else None

    u_next = np.zeros(N + 1)

    for n in range(1, n_steps - 1):
        D_curr = u_curr[2:] - 2 * u_curr[1:-1] + u_curr[:-2]
        D_prev = u_prev[2:] - 2 * u_prev[1:-1] + u_prev[:-2]
        v = u_curr[1:-1] - u_prev[1:-1]

        u_next[1:-1] = (
            2 * u_curr[1:-1] - u_prev[1:-1]
            + r**2 * D_curr
            - 2 * p.sigma0 * dt * v
            + 2 * p.sigma1 * dt / dx**2 * (D_curr - D_prev)
        )

        u_next[0] = 0.0
        u_next[-1] = 0.0
        samples[n + 1] = u_next[i_pickup]

        if keep_frames and (n + 1) % frame_every == 0:
            frames.append(u_next.copy())

        u_prev, u_curr, u_next = u_curr, u_next, u_prev

    if frames is not None:
        frames = np.asarray(frames)

    return SimulationResult(
        samples=samples,
        x=x,
        frames=frames,
        c=c,
        dx=dx,
        dt=dt,
        r=r,
        N=N,
        x_pluck=xp,
        x_pickup=x_pickup,
    )

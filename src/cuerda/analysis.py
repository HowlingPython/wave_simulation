import numpy as np


def spectrum(samples, fs):
    w = np.hanning(len(samples))
    y = samples - samples.mean()
    spec = np.abs(np.fft.rfft(y * w))
    freq = np.fft.rfftfreq(len(y), 1 / fs)
    return freq, spec


def fourier_prediction(p, result, modes=30):
    M = min(modes, result.N - 1)
    m = np.arange(1, M + 1)

    B = (
        2 * p.amplitude * p.L**2
        * np.sin(m * np.pi * result.x_pluck / p.L)
        / (m**2 * np.pi**2 * result.x_pluck * (p.L - result.x_pluck))
    )

    pred = np.abs(B * np.sin(m * np.pi * result.x_pickup / p.L))
    theta = np.arccos(1 - 2 * result.r**2 * np.sin(m * np.pi / (2 * result.N))**2)
    freqs = theta * p.fs / (2 * np.pi)

    return m, freqs, pred / (pred.max() + 1e-12)


def sampled_harmonics(samples, fs, freqs):
    f, spec = spectrum(samples, fs)

    amps = np.array([
        spec[np.argmin(np.abs(f - fi))]
        for fi in freqs
    ])

    return amps / (amps.max() + 1e-12)


def harmonic_table(p, result, modes=20):
    m, freqs, pred = fourier_prediction(p, result, modes)
    sim = sampled_harmonics(result.samples, p.fs, freqs)
    return list(zip(m, freqs, pred, sim))

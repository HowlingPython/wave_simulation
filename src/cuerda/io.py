from pathlib import Path
import numpy as np
from scipy.io import wavfile


def write_wav(path, samples, fs, gain=0.9, lead_silence=0.25, fade_in=0.005):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    y = samples - samples.mean()

    n_fade = min(len(y), int(fade_in * fs))
    if n_fade > 0:
        y[:n_fade] *= np.linspace(0, 1, n_fade)

    y = y / (np.max(np.abs(y)) + 1e-12)

    n_silence = int(lead_silence * fs)
    if n_silence > 0:
        y = np.concatenate([np.zeros(n_silence), y])

    wavfile.write(path, fs, (gain * 32767 * y).astype(np.int16))
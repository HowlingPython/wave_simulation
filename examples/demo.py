from cuerda.analysis import harmonic_table
from cuerda.config import Params
from cuerda.io import write_wav
from cuerda.model import simulate


p = Params(f1=220, duration=3, pluck_pos=0.2, pickup_pos=0.82)
result = simulate(p)

write_wav("outputs/demo.wav", result.samples, p.fs)

for row in harmonic_table(p, result, modes=10):
    m, freq, pred, sim = row
    print(f"{m:2d} {freq:8.2f} Hz  Fourier={pred:6.3f}  sim={sim:6.3f}")

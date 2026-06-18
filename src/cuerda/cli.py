import argparse
from pathlib import Path

from .analysis import harmonic_table
from .config import Params
from .io import write_wav
from .model import simulate
from .plots import save_animation_html, save_spectrum, show_animation

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--f1", type=float, default=220.0)
    parser.add_argument("--fs", type=int, default=44100)
    parser.add_argument("--duration", type=float, default=3.0)
    parser.add_argument("--pluck", type=float, default=0.2)
    parser.add_argument("--pickup", type=float, default=0.82)
    parser.add_argument("--amplitude", type=float, default=0.5)
    parser.add_argument("--sigma0", type=float, default=0.7)
    parser.add_argument("--sigma1", type=float, default=8e-5)
    parser.add_argument("--wav", default="outputs/cuerda.wav")
    parser.add_argument("--lead-silence", type=float, default=0.25)
    parser.add_argument("--fade-in", type=float, default=0.005)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--animate", nargs="?", const="outputs/cuerda.html")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--fps", type=int, default=60)
    return parser


def main():
    args = build_parser().parse_args()

    p = Params(
        f1=args.f1,
        fs=args.fs,
        duration=args.duration,
        pluck_pos=args.pluck,
        pickup_pos=args.pickup,
        amplitude=args.amplitude,
        sigma0=args.sigma0,
        sigma1=args.sigma1,
    )

    result = simulate(p, keep_frames=args.animate is not None or args.show, fps=args.fps)

    write_wav(
        args.wav,
        result.samples,
        p.fs,
        lead_silence=args.lead_silence,
        fade_in=args.fade_in,
    )

    print(
        f"c={result.c:.2f} | N={result.N} | "
        f"r={result.r:.6f} | wav={args.wav}"
    )

    if args.plot:
        path = Path("outputs/spectrum.png")
        save_spectrum(result.samples, p.fs, path)
        print(f"espectro={path}")

    if args.validate:
        print(" m      freq     Fourier       sim")
        for m, freq, pred, sim in harmonic_table(p, result):
            print(f"{m:2d}  {freq:8.2f}    {pred:7.3f}   {sim:7.3f}")

    if args.animate is not None:
        save_animation_html(result, args.animate, args.fps)
        print(f"animación={args.animate}")
    
    if args.show:
        show_animation(result, args.fps)


if __name__ == "__main__":
    main()

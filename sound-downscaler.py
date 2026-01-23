import numpy as np
import soundfile as sf
import sys

def bit_downscale(audio, bits):
    bits = max(1, min(bits, 16))  # védelem
    levels = 2 ** bits
    step = 2.0 / levels
    return np.round(audio / step) * step

def main(input_wav, output_wav, bits):
    audio, samplerate = sf.read(input_wav, dtype='float32')

    # stereo / mono kompatibilis
    if audio.ndim == 2:
        audio = np.apply_along_axis(bit_downscale, 0, audio, bits)
    else:
        audio = bit_downscale(audio, bits)

    sf.write(output_wav, audio, samplerate)
    print(f"Kész! → {bits} bit")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("How to use it: python sound-downscaler.py input.wav output.wav <bits>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))

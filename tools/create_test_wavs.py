"""Create two short WAV files (1s sine tones) in songs/ for testing playback.
Run this script from the project root.
"""
import os, wave, math, struct

ROOT = os.path.dirname(os.path.dirname(__file__))
SONGS_DIR = os.path.join(ROOT, 'songs')
os.makedirs(SONGS_DIR, exist_ok=True)

def write_wav(path, freq=440.0, duration=1.5, framerate=44100):
    nframes = int(framerate * duration)
    amplitude = 0.3
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(framerate)
        for i in range(nframes):
            sample = int(32767 * amplitude * math.sin(2 * math.pi * freq * i / framerate))
            wf.writeframes(struct.pack('<h', sample))

print('Creating test WAVs in', SONGS_DIR)
write_wav(os.path.join(SONGS_DIR, '1.wav'), freq=440.0)
write_wav(os.path.join(SONGS_DIR, '2.wav'), freq=660.0)
print('Done.')

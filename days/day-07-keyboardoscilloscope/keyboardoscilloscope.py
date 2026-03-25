import numpy as np
import sounddevice as sd
import pygame
import sys

SAMPLE_RATE = 44100
WIDTH, HEIGHT = 800, 400

KEY_FREQS = {
    pygame.K_a: 261.63,
    pygame.K_s: 293.66,
    pygame.K_d: 329.63,
    pygame.K_f: 349.23,
    pygame.K_g: 392.00,
    pygame.K_h: 440.00,
    pygame.K_j: 493.88,
    pygame.K_k: 523.25,
}

active_freqs = set()
phase = 0.0
current_wave = np.zeros(1024)

def audio_callback(outdata, frames, time_info, status):
    global phase, current_wave
    
    freqs = list(active_freqs)
    if not freqs:
        outdata.fill(0)
        current_wave = np.zeros(frames)
        return

    t = (np.arange(frames) + phase) / SAMPLE_RATE
    wave = np.zeros(frames)
    
    for f in freqs:
        wave += np.sin(2 * np.pi * f * t)
        
    wave /= max(len(freqs), 1)
    current_wave = wave.copy()
    outdata[:, 0] = wave
    phase += frames

def draw_oscilloscope(screen):
    screen.fill((20, 20, 20))
    wave = current_wave
    
    if len(wave) == 0:
        pygame.display.flip()
        return

    points = []
    display_samples = min(WIDTH, len(wave))
    step = WIDTH / display_samples

    for i in range(display_samples):
        x = int(i * step)
        y = int(HEIGHT/2 - (wave[i] * (HEIGHT/3)))
        points.append((x, y))
        
    if len(points) > 1:
        pygame.draw.lines(screen, (0, 255, 150), False, points, 2)
        
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("KeyboardOscilloscope")
    
    stream = sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback
    )

    with stream:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in KEY_FREQS:
                        active_freqs.add(KEY_FREQS[event.key])
                elif event.type == pygame.KEYUP:
                    if event.key in KEY_FREQS:
                        active_freqs.discard(KEY_FREQS[event.key])

            draw_oscilloscope(screen)
            pygame.time.delay(16)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

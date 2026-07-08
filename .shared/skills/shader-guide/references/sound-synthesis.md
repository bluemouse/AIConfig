# sound-synthesis: Sound Synthesis

## Guideline


Build procedural audio with a four-layer pipeline: oscillator, envelope, filter, and mix — output amplitude samples per frame in the fragment stage.

## Rationale


1. **Oscillator layer**: `sin(2π·f·t)`, layering harmonics or FM modulation to build timbre
2. **Envelope layer**: `exp(-rate·t)` + `smoothstep` attack, simulating strike→decay
3. **Sequencer layer**: Macro definitions / array lookup / hash pseudo-random for arranging melodies
4. **Effects layer**: Reverb, delay, distortion, filters, and other post-processing

Key formulas:
- MIDI → frequency: `f = 440.0 × 2^((n - 69) / 12)`
- Sine oscillator: `y = sin(2π × freq × time)`
- Exponential decay: `env = exp(-decay_rate × time)`
- FM modulation: `y = sin(2π × f_c × t + depth × sin(2π × f_m × t))`

## How to Apply

1. **Step 1: mainSound Entry Framework** — Define `mainSound(int samp, float time)` returning stereo `vec2` amplitude per sample.
2. **Step 2: MIDI Note to Frequency** — Convert note numbers to Hz with `440 * 2^((n-69)/12)`.
3. **Step 3: Basic Oscillators** — Layer sine/triangle/square sources with per-voice envelope.
4. **Step 4: Additive Synthesis Instrument** — Sum harmonics with decreasing amplitude for timbre.
5. **Step 5: FM Synthesis Instrument** — Modulate carrier phase with modulator sine for bell/piano tones.
6. **Step 6: Percussion Synthesis** — Use noise bursts plus exponential decay for drums and hi-hats.
7. **Step 7: Note Sequence Arrangement** — Schedule notes via macros, arrays, or hash-driven patterns.
8. **Step 8: Chord Construction** — Stack detuned voices at chord intervals for polyphony.
9. **Step 9: Delay and Reverb** — Feed multi-tap delay and comb-filter feedback for space.
10. **Step 10: Beat and Arrangement Structure** — Gate layers by bar/beat phase for song sections.

## Example

```glsl
#define TAU 6.28318530718
#define BPM 120.0
#define SPB (60.0 / BPM)

vec2 mainSound(int samp, float time) {
    vec2 audio = vec2(0.0);
    // Layer each instrument/track
    audio *= 0.5 * smoothstep(0.0, 0.5, time);  // Master volume + pop prevention
    return clamp(audio, -1.0, 1.0);
}
```

```glsl
float noteFreq(float note) {
    return 440.0 * pow(2.0, (note - 69.0) / 12.0);
}
```

```glsl
float osc_sin(float t) { return sin(TAU * t); }
float osc_saw(float t) { return fract(t) * 2.0 - 1.0; }
float osc_sqr(float t) { return step(fract(t), 0.5) * 2.0 - 1.0; }
float osc_tri(float t) { return abs(fract(t) - 0.5) * 4.0 - 1.0; }
```

## Advanced

- **GLSL Fundamentals**: Functions, vector operations, `float`/`vec2` types, math functions like `sin()`/`exp()`/`fract()`
- **Audio Fundamentals**: Sample rate (typically 44100Hz), frequency-to-pitch relationship, waveform concepts (sine, sawtooth, square)
- **Music Theory Basics**: MIDI note numbers, equal temperament, octave relationship (frequency doubles), chord construction
- **Envelope/ADSR Basics**: attack, decay, sustain, release for note articulation.

## Gotchas

- Waveform discontinuities click on phase wrap — crossfade or use continuous functions like `sin(phase)`.
- Sample rate assumed 44.1 kHz in `uTime` scaling detunes on other rates — derive frequency from `uSampleRate` uniform.
- Stereo output from mono synthesis needs pan law — apply `-3 dB` center pan to avoid loudness jump.

## Combine With

- _(standalone technique)_

"""
Procedural sound FX synthesizer using numpy and pygame mixer.
Generates retro & atmospheric sound effects at runtime with zero external asset files needed.
"""
import pygame
import numpy as np

class SoundManager:
    _instance = None

    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._generate_all_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio initialization error: {e}. Running in silent mode.")
            self.enabled = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _generate_all_sounds(self):
        sample_rate = 44100

        def make_sound(samples):
            # samples shape: (N,), values in -1.0 .. 1.0
            stereo = np.column_stack((samples, samples))
            int16_samples = (stereo * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(int16_samples)

        # 1. Card draw / swoosh
        t = np.linspace(0, 0.12, int(sample_rate * 0.12), False)
        env = np.sin(np.pi * t / 0.12)
        noise = np.random.uniform(-0.4, 0.4, len(t))
        sweep = np.sin(2 * np.pi * (200 + 400 * (t / 0.12)) * t) * 0.5
        card_draw = (noise * 0.5 + sweep) * env
        self.sounds['card_draw'] = make_sound(card_draw)

        # 2. Attack / Sword slash
        t = np.linspace(0, 0.22, int(sample_rate * 0.22), False)
        env = (1 - t / 0.22) ** 2
        noise = np.random.uniform(-0.8, 0.8, len(t))
        tone = np.sin(2 * np.pi * (450 - 250 * (t / 0.22)) * t)
        slash = (noise * 0.6 + tone * 0.4) * env
        self.sounds['attack'] = make_sound(slash)

        # 3. Heavy impact / critical hit
        t = np.linspace(0, 0.35, int(sample_rate * 0.35), False)
        env = np.exp(-12 * t)
        sub = np.sin(2 * np.pi * (140 - 80 * t) * t) * 0.8
        noise = np.random.uniform(-0.7, 0.7, len(t)) * np.exp(-18 * t)
        impact = (sub + noise) * env
        self.sounds['heavy_hit'] = make_sound(impact)

        # 4. Shield block / parry
        t = np.linspace(0, 0.25, int(sample_rate * 0.25), False)
        env = np.exp(-14 * t)
        metal = (np.sin(2 * np.pi * 620 * t) * 0.5 + 
                 np.sin(2 * np.pi * 1240 * t) * 0.3 +
                 np.sin(2 * np.pi * 1860 * t) * 0.2)
        block = metal * env
        self.sounds['block'] = make_sound(block)

        # 5. Magic cast / Dark spell
        t = np.linspace(0, 0.45, int(sample_rate * 0.45), False)
        env = np.sin(np.pi * t / 0.45)
        f1 = 280 + 350 * np.sin(2 * np.pi * 5 * t)
        f2 = 420 + 200 * np.cos(2 * np.pi * 7 * t)
        magic = (np.sin(2 * np.pi * f1 * t) * 0.4 + np.sin(2 * np.pi * f2 * t) * 0.4) * env
        self.sounds['magic'] = make_sound(magic)

        # 6. Buff / power gain
        t = np.linspace(0, 0.35, int(sample_rate * 0.35), False)
        env = (1 - t / 0.35) ** 0.8
        freq = 300 + 600 * (t / 0.35)
        buff = np.sin(2 * np.pi * freq * t) * 0.5 * env
        self.sounds['buff'] = make_sound(buff)

        # 7. Debuff / curse
        t = np.linspace(0, 0.4, int(sample_rate * 0.4), False)
        env = (1 - t / 0.4)
        freq = 480 - 320 * (t / 0.4)
        debuff = (np.sin(2 * np.pi * freq * t) * 0.5 + np.sin(2 * np.pi * (freq * 1.414) * t) * 0.3) * env
        self.sounds['debuff'] = make_sound(debuff)

        # 8. Gold coin pickup
        t = np.linspace(0, 0.2, int(sample_rate * 0.2), False)
        env = np.exp(-15 * t)
        coin = (np.sin(2 * np.pi * 987.77 * t) * 0.6 + np.sin(2 * np.pi * 1318.5 * t) * 0.4) * env
        self.sounds['gold'] = make_sound(coin)

        # 9. Button click / select
        t = np.linspace(0, 0.05, int(sample_rate * 0.05), False)
        env = np.exp(-40 * t)
        click = np.sin(2 * np.pi * 700 * t) * 0.4 * env
        self.sounds['click'] = make_sound(click)

        # 10. Victory fanfare
        t = np.linspace(0, 0.6, int(sample_rate * 0.6), False)
        env = np.exp(-3 * t)
        # Chords C-E-G-C
        v = (np.sin(2 * np.pi * 523.25 * t) * 0.3 +
             np.sin(2 * np.pi * 659.25 * t) * 0.3 +
             np.sin(2 * np.pi * 783.99 * t) * 0.3 +
             np.sin(2 * np.pi * 1046.5 * t) * 0.2) * env
        self.sounds['victory'] = make_sound(v)

    def play(self, sound_name: str, volume: float = 0.6):
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            snd = self.sounds[sound_name]
            snd.set_volume(max(0.0, min(1.0, volume)))
            snd.play()
        except Exception:
            pass

def play_sfx(name: str, volume: float = 0.6):
    SoundManager.get_instance().play(name, volume)

from pathlib import Path
import tempfile
import unittest
import wave

from faster_whisper.audio import decode_audio


class AudioDependencyTests(unittest.TestCase):
    def test_faster_whisper_can_decode_a_real_wave_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "silencio.wav"
            with wave.open(str(audio_path), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(16_000)
                audio.writeframes(b"\x00\x00" * 1_600)

            decoded = decode_audio(str(audio_path), sampling_rate=16_000)

            self.assertEqual(decoded.shape, (1_600,))


if __name__ == "__main__":
    unittest.main()

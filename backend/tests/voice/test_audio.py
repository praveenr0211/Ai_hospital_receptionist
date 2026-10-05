"""Tests for audio processing utilities."""

import pytest
from app.voice.audio import AudioProcessor


def test_base64_encode_decode():
    raw = b"\x00\x01\x02\x03\x04\x05"
    encoded = AudioProcessor.encode_base64_payload(raw)
    assert isinstance(encoded, str)
    decoded = AudioProcessor.decode_base64_payload(encoded)
    assert decoded == raw


def test_base64_empty():
    assert AudioProcessor.encode_base64_payload(b"") == ""
    assert AudioProcessor.decode_base64_payload("") == b""


def test_calculate_duration_ms():
    # 16000 samples/sec * 1 channel * 2 bytes/sample = 32000 bytes/sec
    # 32000 bytes = 1000 ms
    duration = AudioProcessor.calculate_duration_ms(32000, sample_rate=16000)
    assert duration == 1000.0

    # 1600 bytes = 50 ms
    duration_50ms = AudioProcessor.calculate_duration_ms(1600, sample_rate=16000)
    assert duration_50ms == 50.0


def test_chunk_pcm_audio():
    # 24000 samples/sec * 1 channel * 2 bytes/sample = 48000 bytes/sec
    # 20ms chunk = 960 bytes
    total_bytes = 960 * 5  # 5 chunks
    raw_pcm = b"\xaa" * total_bytes
    chunks = list(AudioProcessor.chunk_pcm_audio(raw_pcm, chunk_duration_ms=20, sample_rate=24000))
    assert len(chunks) == 5
    for c in chunks:
        assert len(c) == 960


def test_generate_silence():
    # 16kHz, 100ms silence = 3200 bytes
    silence = AudioProcessor.generate_silence(duration_ms=100, sample_rate=16000)
    assert len(silence) == 3200
    assert silence == b"\x00" * 3200


def test_validate_pcm16le():
    assert AudioProcessor.validate_pcm16le(b"\x01\x02") is True
    assert AudioProcessor.validate_pcm16le(b"\x01\x02\x03") is False

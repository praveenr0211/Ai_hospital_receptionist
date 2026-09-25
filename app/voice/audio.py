"""Audio processing utilities for telephony and voice AI streaming.

Handles Base64 encoding/decoding, PCM 16-bit Little-Endian conversions,
duration calculations, and frame chunking.
"""

import base64
import struct
from typing import Iterator


class AudioProcessor:
    """Utilities for processing raw PCM audio frames."""

    @staticmethod
    def decode_base64_payload(payload: str) -> bytes:
        """Decode base64 encoded audio payload received from Exotel AgentStream."""
        if not payload:
            return b""
        return base64.b64decode(payload)

    @staticmethod
    def encode_base64_payload(pcm_bytes: bytes) -> str:
        """Encode raw PCM audio bytes to base64 string for Exotel AgentStream."""
        if not pcm_bytes:
            return ""
        return base64.b64encode(pcm_bytes).decode("utf-8")

    @staticmethod
    def calculate_duration_ms(byte_count: int, sample_rate: int = 16000, channels: int = 1, bytes_per_sample: int = 2) -> float:
        """Calculate the duration of PCM audio in milliseconds."""
        bytes_per_second = sample_rate * channels * bytes_per_sample
        if bytes_per_second == 0:
            return 0.0
        return (byte_count / bytes_per_second) * 1000.0

    @staticmethod
    def chunk_pcm_audio(pcm_bytes: bytes, chunk_duration_ms: int = 20, sample_rate: int = 24000, channels: int = 1, bytes_per_sample: int = 2) -> Iterator[bytes]:
        """Split PCM audio into discrete time-based chunks (e.g., 20ms frames for streaming)."""
        bytes_per_second = sample_rate * channels * bytes_per_sample
        chunk_size = int((bytes_per_second * chunk_duration_ms) / 1000)
        
        # Ensure even alignment for 16-bit samples
        if chunk_size % bytes_per_sample != 0:
            chunk_size += bytes_per_sample - (chunk_size % bytes_per_sample)

        for i in range(0, len(pcm_bytes), chunk_size):
            yield pcm_bytes[i:i + chunk_size]

    @staticmethod
    def generate_silence(duration_ms: int, sample_rate: int = 16000, channels: int = 1, bytes_per_sample: int = 2) -> bytes:
        """Generate silent PCM frames (zeros) for a given duration."""
        bytes_per_second = sample_rate * channels * bytes_per_sample
        total_bytes = int((bytes_per_second * duration_ms) / 1000)
        if total_bytes % bytes_per_sample != 0:
            total_bytes += bytes_per_sample - (total_bytes % bytes_per_sample)
        return b"\x00" * total_bytes

    @staticmethod
    def validate_pcm16le(data: bytes) -> bool:
        """Validate that raw byte sequence aligns with 16-bit little-endian samples."""
        if len(data) % 2 != 0:
            return False
        return True

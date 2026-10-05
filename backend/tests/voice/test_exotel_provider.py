"""Tests for Exotel telephony provider and AgentStream protocol formatting."""

import json
from app.voice.providers.exotel import ExotelProvider


def test_build_inbound_response_json():
    provider = ExotelProvider()
    resp = provider.build_inbound_response(
        call_sid="exotel_123",
        stream_url="wss://hospital.com/stream/exotel_123"
    )
    data = json.loads(resp)
    assert data["status"] == "success"
    assert data["action"] == "connect_stream"
    assert data["call_sid"] == "exotel_123"
    assert data["stream_url"] == "wss://hospital.com/stream/exotel_123"
    assert data["sample_rate"] == 16000


def test_build_inbound_xml():
    provider = ExotelProvider()
    xml_str = provider.build_inbound_xml("wss://hospital.com/stream/exotel_123")
    assert "<Response>" in xml_str
    assert '<Stream url="wss://hospital.com/stream/exotel_123"' in xml_str


def test_create_media_frame():
    raw_pcm = b"\x01\x02\x03\x04"
    frame_str = ExotelProvider.create_media_frame("stream_abc", raw_pcm)
    frame = json.loads(frame_str)
    assert frame["event"] == "media"
    assert frame["stream_sid"] == "stream_abc"
    assert "payload" in frame["media"]


def test_create_clear_frame():
    clear_str = ExotelProvider.create_clear_frame("stream_abc")
    frame = json.loads(clear_str)
    assert frame["event"] == "clear"
    assert frame["stream_sid"] == "stream_abc"


def test_parse_event():
    valid_json = '{"event": "start", "start": {"stream_sid": "str_1"}}'
    event = ExotelProvider.parse_event(valid_json)
    assert event["event"] == "start"
    assert event["start"]["stream_sid"] == "str_1"

    invalid_json = 'not-json'
    error_event = ExotelProvider.parse_event(invalid_json)
    assert error_event["event"] == "error"

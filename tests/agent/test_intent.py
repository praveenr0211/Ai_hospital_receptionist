import pytest
from app.agent.llm import classify_intent, extract_time_str, extract_phone_number

def test_intent_booking():
    res = classify_intent("I need to see a doctor for an appointment")
    assert res.intent == "BOOK_APPOINTMENT"
    assert res.confidence == "high"

def test_intent_booking_via_symptoms():
    res = classify_intent("I have severe tooth pain since yesterday")
    assert res.intent == "BOOK_APPOINTMENT"

def test_intent_cancel():
    res = classify_intent("Can I please cancel my appointment?")
    assert res.intent == "CANCEL_APPOINTMENT"
    assert res.confidence == "high"

def test_intent_reschedule():
    res = classify_intent("I want to change my appointment time to tomorrow")
    assert res.intent == "RESCHEDULE_APPOINTMENT"
    assert res.confidence == "high"

def test_intent_human_agent():
    res = classify_intent("Please connect me to a human operator")
    assert res.intent == "HUMAN_AGENT"

def test_intent_emergency():
    res = classify_intent("I can't breathe and I'm having crushing chest pain")
    assert res.intent == "EMERGENCY"

def test_time_extraction():
    assert extract_time_str("I want 10:30 please") == "10:30"
    assert extract_time_str("Can I come at 10:30 AM?") == "10:30"
    assert extract_time_str("Is 2:30 PM available?") == "14:30"
    assert extract_time_str("Book for 11 AM") == "11:00"

def test_phone_extraction():
    assert extract_phone_number("My phone number is 9876543210") == "9876543210"
    assert extract_phone_number("Call me at +91-9876543210") == "+919876543210"

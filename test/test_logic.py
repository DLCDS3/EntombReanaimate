from logic import condition_fn

from collections import Counter

def test_and_logic():
    hand = Counter({"Island" : 2, "Forest":1})
    logic = [{"type": "AND", "cards": ["Island", "Island"]}]
    assert condition_fn(hand, logic)

def test_and_logic_fail():
    hand = Counter({"Island" : 1, "Forest":1})
    logic = [{"type": "AND", "cards": ["Island", "Island"]}]
    assert not condition_fn(hand, logic)

def test_or_logic():
    hand = Counter({"Island" : 1, "Forest":1})
    logic = [{"type": "OR", "cards": ["Island", "Swamp"]}]
    assert condition_fn(hand, logic)

def test_or_logic_fail():
    hand =  Counter({"Plains" :1, "Forest" :1})
    logic = [{"type": "OR", "cards": ["Island", "Swamp"]}]
    assert not condition_fn(hand, logic)

def test_not_logic():
    hand = Counter({"Plains" :1, "Forest" :1})
    logic = [{"type": "NOT", "cards": ["Swamp"]}]
    assert condition_fn(hand, logic)

def test_not_logic_fail():
    hand = Counter({"Swamp" :1, "Forest" :1})
    logic = [{"type": "NOT", "cards": ["Swamp"]}]
    assert not condition_fn(hand, logic)

def test_combined_logic():
    hand = Counter({"Island" : 2, "Forest":1})
    logic = [
        {"type": "AND", "cards": ["Island", "Island"]},
        {"type": "OR", "cards": ["Forest", "Swamp"]},
        {"type": "NOT", "cards": ["Mountain"]}
    ]
    assert condition_fn(hand, logic)

def test_combined_logic_multiple_or():
    hand = Counter({"Island" : 2, "Forest":1})
    logic = [
        {"type": "OR", "cards": ["Island", "Forest"]},
        {"type": "OR", "cards": ["Island", "Forest"]},
        {"type": "AND", "cards": ["Island"]}
    ]
    assert condition_fn(hand, logic)

def test_combined_logic_multiple_or_revserse():
    hand = Counter({"Island" : 1, "Forest":1})
    logic = [
        {"type": "OR", "cards": ["Island", "Forest"]},
        {"type": "OR", "cards": ["Island", "Forest"]},
        {"type": "AND", "cards": ["Island"]}
    ]
    assert not condition_fn(hand, logic)

def test_combined_logic_multiple_or_order():
    hand = Counter({"Island" : 2, "Forest":1})
    logic = [
        {"type": "OR", "cards": ["Forest","Island"]},
        {"type": "OR", "cards": ["Forest","Island"]},
        {"type": "AND", "cards": ["Island"]}
    ]
    assert condition_fn(hand, logic)
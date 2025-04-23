from collections import Counter
from typing import List

def condition_fn(hand_counter: Counter, logic_groups: List[dict]) -> bool:
    # Making sure AND being handled first
    logic_groups = sorted(logic_groups, key=lambda x: 0 if x["type"] == "AND" else 1)

    for group in logic_groups:
        typ = group['type']
        req = Counter(group['cards'])
        if typ == 'AND':
            if any(hand_counter[c] < cnt for c, cnt in req.items()):
                return False
            hand_counter -= req

        elif typ == 'OR':
            if not any(hand_counter[c] >= cnt for c, cnt in req.items()):
                return False
            for c,cnt in req.items():
                if hand_counter[c] >= cnt:
                    hand_counter[c] -= req[c]
                    break

        elif typ == 'NOT':
            if any(hand_counter[c] > 0 for c in req):
                return False
            
    return True
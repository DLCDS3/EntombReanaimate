from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from collections import Counter
import uvicorn
import numpy as np
import os
import json

app = FastAPI()

# Ensure directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Write the index.html template
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Entomb+Reanimate</title>
    <style>
        .logic-group { border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }
        .card-select-wrapper { margin-bottom: 5px; }
    </style>
    <script>
    let deckFull = [];
    let deckUnique = [];

    async function uploadDeck(event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("deckfile", document.getElementById("deckfile").files[0]);

        const res = await fetch("/upload", { method: "POST", body: formData });
        const data = await res.json();
        deckFull = data.full_deck;
        deckUnique = data.unique_deck;

        document.getElementById("logicBuilder").style.display = "block";
        document.getElementById("logicGroups").innerHTML = "";
    }

    function addLogicGroup() {
        const groupContainer = document.createElement("div");
        groupContainer.className = "logic-group";
        groupContainer.innerHTML = `
            <label>Logic Type:</label>
            <select class="logic-type">
                <option value="AND">AND</option>
                <option value="OR">OR</option>
                <option value="NOT">NOT</option>
            </select>
            <div class="card-selects"></div>
            <button type="button" class="add-card-btn">Add Card</button>
            <button type="button" class="remove-group-btn">Remove Group</button>
        `;
        document.getElementById("logicGroups").appendChild(groupContainer);

        groupContainer.querySelector(".add-card-btn").onclick = () => addCardSelect(groupContainer);
        groupContainer.querySelector(".remove-group-btn").onclick = () => groupContainer.remove();
        addCardSelect(groupContainer);
    }

    function addCardSelect(groupContainer) {
        const cardsDiv = groupContainer.querySelector(".card-selects");
        const wrapper = document.createElement("div");
        wrapper.className = "card-select-wrapper";
        wrapper.innerHTML = `
            <select class="card-select">
                <option value="">-- none --</option>
            </select>
            <button type="button" class="remove-card-btn">Remove</button>
        `;
        cardsDiv.appendChild(wrapper);
        const select = wrapper.querySelector("select");
        deckUnique.forEach(card => {
            const opt = document.createElement("option"); opt.value = card; opt.text = card;
            select.add(opt);
        });
        wrapper.querySelector(".remove-card-btn").onclick = () => wrapper.remove();
    }

    async function runSimulation() {
        const groups = [];
        document.querySelectorAll(".logic-group").forEach(group => {
            const type = group.querySelector(".logic-type").value;
            const cards = Array.from(group.querySelectorAll(".card-select"))
                .map(s => s.value).filter(c => c);
            if (cards.length) groups.push({ type, cards });
        });

        const payload = { deck: deckFull, logic: groups };
        const res = await fetch("/simulate", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (!res.ok) {
            document.getElementById("result").innerText = `Error: ${result.detail || JSON.stringify(result)}`;
        } else {
            document.getElementById("result").innerText =
                `Probability: ${(result.probability * 100).toFixed(2)}%`;
        }
    }
    </script>
</head>
<body>
    <h1>Entomb+Reanimate</h1>
    <form id="uploadForm" onsubmit="uploadDeck(event)">
        <input type="file" id="deckfile" name="deckfile" required>
        <input type="submit" value="Upload Deck">
    </form>

    <div id="logicBuilder" style="display:none">
        <h3>Define Logic Groups</h3>
        <div id="logicGroups"></div>
        <button type="button" onclick="addLogicGroup()">Add Logic Group</button>
        <button type="button" onclick="runSimulation()">Run Simulation</button>
        <div id="result"></div>
    </div>
</body>
</html>
""")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
def upload_deck(deckfile: UploadFile = File(...)):
    content = deckfile.file.read().decode("utf-8")
    deck_full = parse_deck(content)
    unique_deck = sorted(set(deck_full))
    return {"full_deck": deck_full, "unique_deck": unique_deck}

@app.post("/simulate")
async def simulate(data: Dict = Body(...)):
    deck_full: List[str] = data.get("deck", [])
    logic_groups: List[Dict] = data.get("logic", [])

    # Validate requested copies
    deck_counter = Counter(deck_full)
    combined = Counter()

    for group in logic_groups:
        req = Counter(group['cards'])
        if group['type'] == 'ADD':
            combined += req
            for card, count in combined.items():
                if count > deck_counter.get(card, 0):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Requested {count} copies of '{card}', but deck contains {deck_counter.get(card,0)}"
                    )
            for card, count in req.items():
                if count > deck_counter.get(card, 0):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Requested {count} copies of '{card}', but deck contains {deck_counter.get(card,0)}"
                    )
        if group['type'] != 'ADD':
             for card, count in combined.items():
                 if count > 1:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Requested {count} copies of '{card}' in group {group['type']}, which is not allowed"
                    )                     
    
    

        

    # Label each copy uniquely
    deck_labeled = []
    for card, cnt in deck_counter.items():
        for i in range(cnt):
            deck_labeled.append(f"{card}::{i}")
    deck_np = np.array(deck_labeled)


            
    # Condition function using Counter
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

    success = 0
    trials = 100000
    for _ in range(trials):
        draw = np.random.choice(deck_np, size=7, replace=False)
        hand = [d.split("::")[0] for d in draw]
        hand_counter = Counter(hand)
        if condition_fn(hand_counter,logic_groups):
            success += 1

    return {"probability": success / trials}


def parse_deck(deck_text: str) -> List[str]:
    lines = deck_text.strip().splitlines()
    main_deck = []
    for line in lines:
        if line.strip().lower() == "sideboard":
            break
        if line.strip():
            parts = line.strip().split(" ", 1)
            if len(parts) == 2 and parts[0].isdigit():
                count, name = parts
                main_deck.extend([name] * int(count))
    return main_deck

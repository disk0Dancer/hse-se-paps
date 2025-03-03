"""
This module implements a simple FastAPI app demonstrating:
- KISS: Keep endpoints straightforward.
- YAGNI: Only implement what is strictly necessary.
- DRY: Avoid repetition, use helper functions for repeated logic.
- SOLID: Single Responsibility for each function, etc.
"""

from fastapi import FastAPI, HTTPException

app = FastAPI()

fake_db = {}  # KISS/YAGNI: Just a dict, no extra complexity

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "value": fake_db[item_id]}

@app.post("/items/{item_id}")
def create_item(item_id: int, value: str):
    if item_id in fake_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item_id] = value
    return {"status": "created", "item_id": item_id, "value": value}

@app.put("/items/{item_id}")
def update_item(item_id: int, value: str):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    fake_db[item_id] = value
    return {"status": "updated", "item_id": item_id, "value": value}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[item_id]
    return {"status": "deleted", "item_id": item_id}

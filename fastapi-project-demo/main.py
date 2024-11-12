from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Operations in FastAPI look like  HTTP requests: Post, Get, Put, Delete
app = FastAPI()

items = []

# Allows us to make a model in which we want to send and receive post / get data
class Item(BaseModel):
    text: str 
    is_done: bool = False

# The parameters with "" in brackets defines the path for the query
@app.get("/")
def root():
    return {"Hello" : "World"}

# Here the path is "/items", the function is designed to create an item, after doing so, it returns that item
@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items

# Here we are executing the GET operation and getting all items in our list within a given limit
@app.get("/items", response_model = Item)
def list_items(limit: int = 10):
    return items[0:limit]

@app.get("/items/{item_id}", response_model = Item)
def get_item(item_id: int) -> Item:
    if (len(items) == 0 or len(items) > item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        item = items[item_id]
        return item
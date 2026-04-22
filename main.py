"""
create a simple api which creates a in mem que of ints and a arr of result
/->basic web UI displaying queue and results
/digest -> pop k element and return them
/append -> push a item to que {number,id} here id is for the user who want to add this number
/result -> push the {number,id} into reult
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

# In-memory storage
queue: List[dict] = []
results: List[dict] = []

class Item(BaseModel):
    number: int
    id: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = f"""
    <html>
        <head>
            <title>Queue and Results UI</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 2rem; background: #f4f4f9; color: #333; }}
                h1 {{ text-align: center; color: #4a4e69; }}
                .container {{ display: flex; gap: 2rem; max-width: 800px; margin: 0 auto; }}
                .box {{ flex: 1; background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 400px; overflow-y: auto; }}
                h2 {{ margin-top: 0; color: #22223b; border-bottom: 2px solid #f2e9e4; padding-bottom: 0.5rem; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ background: #f8f9fa; margin-bottom: 0.5rem; padding: 0.75rem; border-radius: 4px; border-left: 4px solid #4a4e69; }}
                .meta {{ font-size: 0.85em; color: #6c757d; }}
                .number {{ font-weight: bold; font-size: 1.1em; }}
            </style>
        </head>
        <body>
            <h1>Queue & Results Dashboard</h1>
            <div class="container">
                <div class="box">
                    <h2>Queue ({len(queue)})</h2>
                    <ul>
                        {''.join(f"<li><div class='number'>Number: {item['number']}</div><div class='meta'>ID: {item['id']}</div></li>" for item in queue)}
                        { '<li>No items in queue.</li>' if not queue else '' }
                    </ul>
                </div>
                <div class="box">
                    <h2>Results ({len(results)})</h2>
                    <ul>
                        {''.join(f"<li><div class='number'>Number: {item['number']}</div><div class='meta'>ID: {item['id']}</div></li>" for item in results)}
                        { '<li>No items in results.</li>' if not results else '' }
                    </ul>
                </div>
            </div>
            <script>
                // Auto-refresh every 2 seconds to see updates live
                setTimeout(() => location.reload(), 2000);
            </script>
        </body>
    </html>
    """
    return html_content

@app.get("/digest")
def digest_items(k: int = Query(1, description="Number of elements to pop")):
    popped = []
    # Pop up to k elements from the front of the queue
    for _ in range(min(k, len(queue))):
        if queue:
            popped.append(queue.pop(0))
    return {"popped": popped}

@app.post("/append")
def append_item(item: Item):
    queue.append(item.model_dump())
    return {"message": "Item appended to queue", "item": item}

@app.post("/result")
def add_result(item: Item):
    results.append(item.model_dump())
    return {"message": "Item added to results", "item": item}

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()

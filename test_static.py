from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(root_path="/temp")
app.mount("/assets", StaticFiles(directory="UI/dist/assets"), name="assets")

@app.get("/")
async def root():
    return {"message": "hello"}

if __name__ == "__main__":
    uvicorn.run("test_static:app", host="0.0.0.0", port=8081)

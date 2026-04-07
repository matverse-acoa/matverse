import uvicorn
from fastapi import FastAPI
import gradio as gr

from .config import APP_NAME, HOST, PORT
from .api import app as api_app
from .ui import create_ui

app = FastAPI(title=APP_NAME)

# Mount the API endpoints
app.mount("/api", api_app)

# Mount the Gradio UI
demo = create_ui()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)

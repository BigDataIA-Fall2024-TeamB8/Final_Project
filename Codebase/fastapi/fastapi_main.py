from fastapi import FastAPI
from agent import (
    search_talks_agent,
    rag_agent,
    web_search_agent,
    note_taking_agent,
    mind_map_agent,
    compare_talks_agent,
)

app = FastAPI(title="AI-Powered TED Talk Assistant")

@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to the AI-Powered TED Talk Assistant API!"}

@app.post("/search")
async def search_talks(query: str):
    """
    Search for TED Talks based on a user query.
    """
    return search_talks_agent(query)

@app.post("/rag")
async def rag_query(question: str):
    """
    Perform a Retrieval-Augmented Generation query.
    """
    return rag_agent(question)

@app.post("/web-search")
async def web_search(query: str):
    """
    Perform a web search and summarize findings.
    """
    return web_search_agent(query)

@app.post("/notes")
async def take_notes(transcript: str, highlight: str):
    """
    Generate notes from a TED Talk transcript.
    """
    return note_taking_agent(transcript, highlight)

@app.post("/mind-map")
async def generate_mind_map(talk_transcript: str):
    """
    Generate a mind map for a TED Talk transcript.
    """
    return mind_map_agent(talk_transcript)

@app.post("/comparison")
async def compare_talks(talk1_transcript: str, talk2_transcript: str):
    """
    Compare themes between two TED Talks.
    """
    return compare_talks_agent(talk1_transcript, talk2_transcript)

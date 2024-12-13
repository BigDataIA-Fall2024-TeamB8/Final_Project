from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, Action as CopilotAction
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi import Query, HTTPException
from agent import generate_transcript
from agent import get_related_talks_agent
from agent import fetch_metadata_from_s3
from agent import extract_slug_from_url
from agent import get_trending_talks_agent
from agent import generate_playbook, fetch_metadata_from_s3
from agent import extract_themes_from_transcript
from agent import fetch_transcript_by_slug
from agent import generate_mind_map
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends
import logging

from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
import operator


import pyodbc
import uuid
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse


import openai
import os
from graphviz import Source
from agent import (
    search_talks_agent,
    chatbot_agent,
    web_search_agent,
    compare_talks_agent,
    s3_client,  
    json
)

app = FastAPI(title="AI-Powered TED Talk Assistant")

logger = logging.getLogger("app_logger")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment Variables
openai_api_key = os.getenv("OPENAI_API_KEY", "default_openai_api_key")  # Replace with default or remove for production
S3_BUCKET = os.getenv("S3_BUCKET", "default_bucket_name")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Replace with a strong key for production
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

RDS_ENDPOINT = os.getenv("RDS_ENDPOINT", "default_rds_endpoint")
RDS_USERNAME = os.getenv("RDS_USERNAME", "default_rds_username")
RDS_PASSWORD = os.getenv("RDS_PASSWORD", "default_rds_password")
RDS_DATABASE = os.getenv("RDS_DATABASE", "default_rds_database")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={RDS_ENDPOINT},1433;"
        f"DATABASE={RDS_DATABASE};"
        f"UID={RDS_USERNAME};"
        f"PWD={RDS_PASSWORD}"
    )


def hash_password(password: str):
    return pwd_context.hash(password)

# Utility to verify passwords
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Utility to create JWT tokens
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decode JWT token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Pydantic models for request validation
class SearchQuery(BaseModel):
    query: str

class QAQuery(BaseModel):
    url: str
    question: str

class CompareQuery(BaseModel):
    talk1: str
    talk2: str

class NotesQuery(BaseModel):
    url: str
    notes: str

class ChatbotRequest(BaseModel):
    message: str

class ChatRequest(BaseModel):
    message: str

class ThemesRequest(BaseModel):
    transcript: str

class ThemesRequest(BaseModel):
    transcript: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserSignup(BaseModel):
    username: str
    password: str
    email: str


class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check user credentials
    cursor.execute("SELECT username, password FROM Users WHERE username = ?", (form_data.username,))
    user_record = cursor.fetchone()
    conn.close()

    if not user_record or not verify_password(form_data.password, user_record[1]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Logout endpoint (stateless)
@app.post("/logout")
def logout():
    # For JWTs, logout is stateless; client-side should discard the token.
    return {"message": "Successfully logged out"}

# Get current user
@app.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    username = decode_access_token(token)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username, Email_ID FROM Users WHERE username = ?", (username,))
    user_record = cursor.fetchone()
    conn.close()

    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"username": user_record[0], "email": user_record[1]}

@app.post("/signup")
def signup(user: UserSignup):
    """
    Signup endpoint to create a new user in the database.

    Args:
        user (UserSignup): A Pydantic model containing `username`, `password`, and `email`.

    Returns:
        dict: A success message if the signup is successful.
    """
    conn = None
    try:
        # Hash the user's password
        hashed_password = hash_password(user.password)

        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user already exists in the database
        cursor.execute("SELECT * FROM Users WHERE username = ?", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User already exists")

        # Insert the new user's credentials into the database
        cursor.execute(
            "INSERT INTO Users (username, password, Email_ID) VALUES (?, ?, ?)",
            (user.username, hashed_password, user.email),
        )
        conn.commit()

        return {"message": "User signed up successfully!"}

    except pyodbc.Error as e:
        logger.error("Signup failed: %s", e)
        raise HTTPException(status_code=500, detail="Signup failed due to a database error")
    
    except Exception as e:
        logger.error("Unexpected error during signup: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
    finally:
        # Ensure the database connection is closed
        if conn:
            conn.close()



@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Powered TED Talk Assistant API!"}

@app.get("/trending")
async def get_trending_talks():
    """
    Endpoint to fetch the top trending TED Talks.
    """
    try:
        # Call the agent to fetch trending talks
        trending_talks = get_trending_talks_agent(top_k=6)
        return {"talks": trending_talks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trending talks: {str(e)}")

@app.get("/related")
async def get_related_talks(slug: str):
    """
    Fetch related TED Talks based on the slug of the selected TED Talk.

    Args:
        slug (str): The slug of the selected TED Talk.

    Returns:
        dict: A dictionary containing a list of related talks.
    """
    try:
        # Fetch related talks using the agent
        related_talks = get_related_talks_agent(slug)

        return {"talks": related_talks}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving related talks: {str(e)}")


# Updated endpoint to handle nested structure
@app.post("/chatbot")
async def chatbot_endpoint(request: Request):
    """
    Chatbot endpoint to handle user messages and route to appropriate LangGraph agents.
    """
    try:
        # Parse the incoming JSON request
        body = await request.json()
        user_message = body.get("message")  # Extract the message from the request

        if not user_message:
            raise HTTPException(status_code=400, detail="Message field is required.")

        # Define system instructions for routing
        system_prompt = """
        You are a TED Talk assistant with access to multiple agents:
        - QA Agent: To answer questions about specific TED Talks using metadata and transcripts.
        - Comparison Agent: To compare two TED Talks and provide a detailed report.
        - Web Search Agent: To fetch additional information from the web for queries.
        
        Analyze the user's query and route it to the appropriate agent. If the query:
        - Mentions two talks or asks for a comparison, use the Comparison Agent.
        - Is a single question about a TED Talk, use the QA Agent.
        - Requires external context, use the Web Search Agent.
        """

        # Parse user query for agent routing
        if "compare" in user_message or "difference" in user_message:
            # Comparison query
            parts = user_message.split("and")
            if len(parts) != 2:
                raise HTTPException(
                    status_code=400,
                    detail="Comparison queries must include exactly two talks separated by 'and'.",
                )
            talk1, talk2 = map(str.strip, parts)
            result = compare_talks_agent(talk1, talk2)
            agent_response = result.get("report", "Comparison failed.")
        elif "search" in user_message or "find" in user_message:
            # Web Search query
            query = user_message.replace("search", "").replace("find", "").strip()
            agent_response = web_search_agent(query)
        else:
            # QA query
            slug = extract_slug_from_url(user_message)
            question = "What is this TED Talk about?"
            agent_response = chatbot_agent(slug, question)

        # Return the response in the expected format
        return JSONResponse(
            content={
                "messages": [
                    {
                        "role": "assistant",
                        "content": agent_response,
                    }
                ]
            }
        )
    except Exception as e:
        print(f"Error in chatbot endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred.")






@app.get("/full_transcript")
async def get_transcript(slug: str):
    """
    Endpoint to fetch the raw transcript for a TED Talk.

    Args:
        slug (str): The slug of the TED Talk.

    Returns:
        dict: A dictionary containing the raw transcript.
    """
    try:
        transcript = generate_transcript(slug)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transcript: {str(e)}")










    

@app.post("/search")
async def search_talks(search_query: SearchQuery):
    try:
        return search_talks_agent(search_query.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qa")
async def qa_endpoint(qa_query: QAQuery):
    try:
        return {"answer": chatbot_agent(qa_query.url, qa_query.question)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/web_search")
async def web_search_endpoint(search_query: SearchQuery):
    try:
        summary = web_search_agent(search_query.query)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
async def compare_talks(compare_query: CompareQuery):
    try:
        report = compare_talks_agent(compare_query.talk1, compare_query.talk2)
        if isinstance(report, dict) and "report" in report:
            return {"report": report["report"]}  # Ensure the response is a string
        raise HTTPException(status_code=500, detail="Invalid report format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/mind_map")
async def get_mind_map(slug: str = Query(..., description="The slug of the TED Talk")):
    """
    Generate a mind map for a TED Talk based on its transcript.
    """
    transcript = fetch_transcript_by_slug(slug)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found.")

    output_png_path = f"/tmp/{slug}_mind_map"
    try:
        generate_mind_map(transcript, output_png_path)
        return FileResponse(f"{output_png_path}.png", media_type="image/png", filename=f"{slug}_mind_map.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating mind map: {e}")






@app.get("/playbooks")
async def get_playbooks():
    """
    Retrieve all saved playbooks from S3.
    """
    try:
        # List all playbook objects in the S3 bucket
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="playbooks/")
        playbooks = []

        for obj in response.get("Contents", []):
            key = obj["Key"]
            playbook_data = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
            playbook = json.loads(playbook_data["Body"].read().decode("utf-8"))
            
            # Add an ID derived from the S3 key
            playbook["id"] = key.split("/")[-1].split(".")[0]  # Extract the unique ID from the filename
            playbooks.append(playbook)

        return {"playbooks": playbooks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving playbooks: {str(e)}")


@app.get("/playbooks/{id}")
async def get_playbook(id: str):
    """
    Retrieve a specific playbook by its ID from S3.
    """
    try:
        # Define the S3 key for the specific playbook
        key = f"playbooks/{id}.json"

        # Fetch the playbook data from S3
        playbook_data = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        playbook = json.loads(playbook_data["Body"].read().decode("utf-8"))

        return playbook
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="Playbook not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving playbook: {str(e)}")



@app.post("/themes")
async def themes_endpoint(request: ThemesRequest):
    """
    Extract themes or buzzwords for a TED Talk using its slug.

    Args:
        request (ThemesRequest): Contains the TED Talk slug or transcript.

    Returns:
        JSON: Extracted themes as a list.
    """
    try:
        # Fetch transcript from S3 based on the slug
        transcript = fetch_transcript_by_slug(request.transcript)
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found.")

        # Extract themes from the transcript
        themes = extract_themes_from_transcript(transcript)
        return {"themes": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting themes: {str(e)}")

@app.delete("/playbooks/{slug}")
async def delete_playbook(slug: str):
    """
    Delete a playbook by its slug.
    """
    try:
        key = f"playbooks/{slug}.json"
        s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
        return {"message": "Playbook deleted successfully"}
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="Playbook not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting playbook: {str(e)}")



@app.post("/generate_playbook")
async def generate_playbook_endpoint(data: NotesQuery):
    """
    Endpoint to generate and save a playbook for a TED Talk.
    """
    try:
        # Generate a unique ID for the playbook
        playbook_id = str(uuid.uuid4())

        # Extract the TED Talk slug from the URL
        slug = extract_slug_from_url(data.url)

        # Fetch metadata from S3 for the TED Talk
        metadata = fetch_metadata_from_s3(S3_BUCKET, slug)
        if "error" in metadata:
            raise HTTPException(status_code=404, detail=f"Metadata not found for {data.url}")

        # Generate the playbook using the agent function
        playbook = generate_playbook(
            url=data.url,
            notes=data.notes,
            transcript=metadata.get("transcript", ""),
            title=metadata.get("title", "N/A"),
            speaker=metadata.get("speakers", "N/A"),
        )

        # Add the ID to the playbook
        playbook["id"] = playbook_id

        # Save the playbook as a JSON file in S3
        playbook_key = f"playbooks/{playbook_id}.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=playbook_key,
            Body=json.dumps(playbook),  # Serialize playbook to JSON
            ContentType="application/json",
        )

        return {"message": "Playbook saved successfully!", "playbook": playbook}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating playbook: {str(e)}")

    
# Define backend actions for CopilotKit
async def fetch_ted_talk_data(query: str):
    return search_talks_agent(query)

async def perform_comparison(talk1: str, talk2: str):
    return compare_talks_agent(talk1, talk2)

# Define CopilotKit actions
actions = [
    CopilotAction(
        name="fetchTedTalkData",
        description="Fetch TED Talks based on a search query.",
        parameters=[{"name": "query", "type": "string", "description": "Search query", "required": True}],
        handler=fetch_ted_talk_data,
    ),
    CopilotAction(
        name="compareTedTalks",
        description="Compare two TED Talks based on their metadata.",
        parameters=[
            {"name": "talk1", "type": "string", "description": "URL of the first TED Talk", "required": True},
            {"name": "talk2", "type": "string", "description": "URL of the second TED Talk", "required": True},
        ],
        handler=perform_comparison,
    ),
    CopilotAction(
        name="answerTedTalkQuery",
        description="Answer a user question about a TED Talk.",
        parameters=[
            {"name": "talk_url", "type": "string", "required": True},
            {"name": "question", "type": "string", "required": True},
        ],
        handler=chatbot_agent,
    ),
]

# Initialize CopilotKit SDK
sdk = CopilotKitSDK(actions=actions)

# Add CopilotKit endpoint to FastAPI
add_fastapi_endpoint(app, sdk, "/copilotkit_remote")

# Main entry point for server
def main():
    import uvicorn
    uvicorn.run("fastapi_main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()

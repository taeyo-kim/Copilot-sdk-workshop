"""
app.py — GitHub Issue Complexity Analyser

Built step-by-step during the livestream. Frontend is pre-built in src/static/.

Usage:
  python app.py hello                          # Phase 2a: Simplest SDK call
  python app.py hello-stream                   # Phase 2b: Streaming events
  python app.py <github_issue_url>             # Phase 4: CLI analysis
  python app.py <owner> <repo> <issue_number>  # Phase 4: CLI analysis
  python app.py serve                          # Phase 5: Start web UI (post via the UI button)
"""


# =================================================================
# PHASE  — Get your access token
# =================================================================
    # Copy the .env example file and call it .env
    # Make a Personal Access Token
    # Paste the token into the .env file


# =================================================================
# PHASE 1 — Imports
# =================================================================

import asyncio
import base64
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from copilot import CopilotClient, define_tool
from copilot.session import PermissionHandler

# Load environment variables from .env file (GITHUB_TOKEN, etc.)
load_dotenv()


# =================================================================
# PHASE 2a — Hello World with send_and_wait (simplest possible)
#
# Three concepts: Client → Session → Response
# send_and_wait() blocks until the full response is ready.
# =================================================================

async def hello_world():
    """Simplest example: send a prompt, get the full response back."""
    pass



# Command to run this phase: python app_final.py hello


# =================================================================
# PHASE 2b — Streaming with Events
#
# Same thing, but now we see tokens arrive in real-time.
# This is the pattern we'll use for the rest of the stream.
# Event types: assistant.message, tool.call, session.idle
# =================================================================

async def hello_world_streaming():
    """Stream the response token by token using events."""
    
    # Setting up our client and session is the same as before
    client = CopilotClient()
    await client.start()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    session = await client.create_session(
        model="gpt-4.1",
        on_permission_request=PermissionHandler.approve_all,
        github_token=token,
    )

    ### Now we add event handlers to see the response as it comes in. ###
    # The SDK emits events as the session runs. We listen for:



    # Register the event handler before sending the message



    # Wait until the session is idle (response is complete) before proceeding.



# Command to run this phase: python app_final.py hello-stream



# =================================================================
# PHASE 3 — Custom Tools with @define_tool
#
# Tools let the agent interact with the outside world.
# You define a function + Pydantic params, and the agent decides
# when and how to call it. That's the "agentic" part.
# =================================================================


# Here's one we prepared earlier - a helper function to call the GitHub API.
# We'll use this inside our tools to fetch issue details, repo structure, search code, and read file contents.
def github_api(endpoint: str) -> dict:
    """Call the GitHub REST API (shared helper for all tools)."""
    import httpx

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "copilot-livestream",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with httpx.Client() as http:
        resp = http.get(f"https://api.github.com{endpoint}", headers=headers)
        resp.raise_for_status()
        return resp.json()



#####################################
# --- Tool 1: Fetch issue details ---

# We use Pydantic to define the expected parameters for the tool. 
# This lets the SDK handle parsing from the various formats the agent might send (dict, JSON string, or Pydantic
class GetIssueParams(BaseModel):
    pass

# The @define_tool decorator registers the function as a tool the agent can call. 
# The description helps the agent understand when to use it.
@define_tool(description="Fetch a GitHub issue including title, body, labels, and comments")
async def get_github_issue(params: GetIssueParams) -> str:
    pass



########################################
# --- Tool 2: Explore repo structure ---

class RepoStructureParams(BaseModel):
    pass

@define_tool(description="List the directory contents of a GitHub repository")
async def get_repo_structure(params: RepoStructureParams) -> str:
    pass



#############################
# --- Tool 3: Search code ---

class SearchCodeParams(BaseModel):
    pass

@define_tool(description="Search for code in a GitHub repository")
async def search_code_in_repo(params: SearchCodeParams) -> str:
    pass



####################################
# --- Tool 4: Read file contents ---

class FileContentParams(BaseModel):
    pass


@define_tool(description="Fetch and read a specific file from a GitHub repository")
async def get_file_content(params: FileContentParams) -> str:
    pass


# =================================================================
# PHASE 4 — System Prompt + CLI Analyser
#
# The system prompt shapes the agent's behaviour. The tools list
# tells the SDK what the agent CAN do. The agent autonomously
# decides WHICH tools to call and in what order.
# =================================================================

### List the tools we just made ###

# TOOLS = 


### Create the system prompt that guides the agent's behaviour. ###
# This is where you inject the "personality" and instructions for the agent. 
# You can include formatting instructions, reasoning steps, and any constraints or guidelines

# SYSTEM_PROMPT = 


# This function is much like Phase 2b, but now the agent can 
# call tools, has a system prompt, and has logic to handle output for different tool calls
async def analyse_cli(owner: str, repo: str, issue_number: int):
    """Run analysis in the terminal with streaming output."""
    print(f"\n🔍 Analysing issue #{issue_number} in {owner}/{repo}...\n") # Just a print to show we have started

    client = CopilotClient()
    await client.start()

    # session setup is nearly the same as before, but now we include our system prompt and tools list.
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    session = await client.create_session(
        model="gpt-4.1",
        tools=TOOLS, # We declare our list of tools here 
        on_permission_request=PermissionHandler.approve_all,
        github_token=token,
    )

    # Set up the event handlers again
    done = asyncio.Event()

    # Handle the different types of events the SDK emits. This include tool calls now.
    # Events might have parameters this time, so this is slightly more complex than before. 
    # (The helper function _parse_args at the bottom can handle the various formats the SDK might give us.)




    # Send a message, now using your system prompt and the specific issue to analyse. 







# Command to run this phase: python app.py <owner> <repo> <issue_number>
# Example: python app.py reneenoble demo_project_with_issues 9


# =================================================================
# PHASE 5 — FastAPI + Server-Sent Events
#
# SSE lets us stream the agent's thinking to the browser in
# real-time. Each tool call and message chunk becomes an event
# the pre-built frontend renders as chat bubbles.
# =================================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI(title="GitHub Issue Complexity Analyser")

# Serve the pre-built frontend
static_dir = Path(__file__).parent / "src" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Serve the main HTML page, where the user can input a GitHub issue URL and trigger the analysis.


# A simple health check endpoint to verify the server is running.


# Endpoint to start the analysis and stream results back to the frontend. 
# This is the route we care about the most, it will stream the analysis results to the frontend
# It will call the function that we'll write below





# There is a helper function _parse_args we wrote for you (at the bottom of the file) that you can use to 
# handle the various formats tool arguments might come in (dict, JSON string, Pydantic model). 


async def stream_analysis(owner: str, repo: str, issue_number: int):
    """Async generator that yields Server-Sent Events for the frontend."""

        # Same session setup as above
    client = CopilotClient()
    await client.start()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    session = await client.create_session(
        model="gpt-4.1",
        tools=TOOLS,
        on_permission_request=PermissionHandler.approve_all,
        github_token=token,
    )


    # Instead of event handling we'll use a queue to collect messages and tool calls, 
    # which we can then stream to the frontend in order.



    # Set up event handling to push messages and tool calls into the queue for streaming to the frontend.
    def on_event(event):
        pass
            # Emitted once per tool invocation, before the tool runs





    # Send off the same message as before, but now the GitHub Issue info has come 
    # from query parameters collected when the analyse/stream endpoint calls this function.




    # Stream events to the frontend as they come in (instead of print to terminal)
    # We'll look for the same events as before (assistant.message and tool.execution_start)




# Command to run this phase: python app.py serve
# Then open http://localhost:8000 in the browser and enter the repo and issue number




# =================================================================
# PHASE 6a — Write Back to GitHub (human-triggered via UI button)
#
# After the analysis streams in, the user reviews it and clicks
# "Post to GitHub". This endpoint posts the comment and adds
# a difficulty label. Human-in-the-loop = safer.
#
# Requires GITHUB_TOKEN with write permissions:
#   - Classic tokens: repo scope
#   - Fine-grained tokens: Issues → Read and Write
# =================================================================

### We've done these one for you for time, but you can try writing your own if you want!###
# The GitHub API docs are here: https://docs.github.com/rest/issues/comments#create-an-issue-comment 
# and here: https://docs.github.com/rest/issues/labels#add-labels-to-an-issue

# These are the labels we'll add based on the recommended skill level the agent outputs in its analysis.
SKILL_LABELS = {
    "junior": ["good first issue", "difficulty: easy"],
    "mid-level": ["difficulty: medium"],
    "senior": ["difficulty: hard"],
    "senior+": ["difficulty: expert"],
}

# These functions use the GitHub REST API to post comments and add labels. 
# The agent will call these when the user clicks the button in the UI.
async def post_comment(owner: str, repo: str, issue_number: int, body: str):
    """Post a comment on a GitHub issue."""
    import httpx

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            json={"body": body},
        )
        resp.raise_for_status()
    print(f"💬 Comment posted to {owner}/{repo}#{issue_number}")


# This function adds labels to the issue based on the recommended skill level the agent outputs in its analysis.
async def add_labels(owner: str, repo: str, issue_number: int, labels: list[str]):
    """Add labels to a GitHub issue."""
    import httpx

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/labels",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            json={"labels": labels},
        )
        resp.raise_for_status()
    print(f"🏷️  Labels added: {', '.join(labels)}")

# The request body for the post_analysis endpoint, 
# which includes the repo and issue info plus the analysis text to post as a comment.
class PostAnalysisRequest(BaseModel):
    owner: str
    repo: str
    issue_number: int
    body: str

# This endpoint is called as part of the "Post to GitHub" button flow in the frontend.
# It takes the analysis text and posts it as a comment, 
# then looks for the recommended skill level in the analysis to determine which labels to add.
@app.post("/post-analysis")
async def post_analysis(req: PostAnalysisRequest):
    """Human-triggered: post the analysis as a comment and add a difficulty label."""
    await post_comment(req.owner, req.repo, req.issue_number, req.body)

    # Pull just the 'Recommended Skill Level' line to avoid matching stray
    # words like 'junior' in the Mentorship Notes. Longest key wins so
    # 'senior+' beats 'senior' and 'mid-level' beats 'mid'.
    import re
    match = re.search(r"recommended skill level.*", req.body, re.IGNORECASE) # Find the line that contains "Recommended Skill Level" and get the level from it
    level_line = match.group(0).lower() if match else ""
    for level in sorted(SKILL_LABELS, key=len, reverse=True):
        # Based on the levels listed in our SKILL_LABELS dict,
        # Find any matching levels to be added as labels on the issue.
        if level in level_line:
            await add_labels(req.owner, req.repo, req.issue_number, SKILL_LABELS[level])
            break

    return {"status": "posted"}


# =================================================================
# PHASE 6b — Safety: Pre-tool Validation Hook (talk through only)
#
# The SDK lets you intercept tool calls BEFORE they execute.
# This is your last line of defense against prompt injection
# or unexpected agent behaviour.
#
# To enable: add "hooks": {"on_pre_tool_use": validate_tool_args}
# to the create_session() calls above.
# =================================================================

# A function that prevents the agent from reading files outside the repo 
# or sensitive files like .env or credentials.

# async def validate_tool_args(event):
#     """Block dangerous tool arguments before execution."""
#     if event.data.tool_name == "get_file_content":
#         path = event.data.arguments.get("path", "")
#         if ".." in path or path.startswith("/") or path.startswith("~"):
#             print(f"  🛑 BLOCKED: unsafe path — {path}")
#             return {"decision": "reject", "message": "Blocked: unsafe path"}
#         sensitive = [".env", ".git/", "secrets", "credentials", "token"]
#         if any(s in path.lower() for s in sensitive):
#             print(f"  🛑 BLOCKED: sensitive file — {path}")
#             return {"decision": "reject", "message": "Blocked: sensitive file"}
#     return {"decision": "allow"}



# =================================================================
# Helper functions
# =================================================================

def parse_github_url(url: str) -> tuple[str, str, int]:
    """Parse 'https://github.com/owner/repo/issues/123' into parts."""
    parts = url.rstrip("/").replace("https://github.com/", "").split("/")
    if len(parts) >= 4 and parts[2] == "issues":
        return parts[0], parts[1], int(parts[3])
    raise ValueError(f"Invalid GitHub issue URL: {url}")


def _parse_args(raw):
    """Parse tool arguments from the various formats the SDK may return."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
    if hasattr(raw, "model_dump"):
        return raw.model_dump()
    return {}



# =================================================================
# CLI Entry Point
# =================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🐛 GitHub Issue Complexity Analyser — Livestream Build\n")
        print("  python app.py hello                          # Test the SDK (send_and_wait)")
        print("  python app.py hello-stream                   # Test with streaming events")
        print("  python app.py <github_issue_url>             # CLI analysis")
        print("  python app.py <owner> <repo> <issue_number>  # CLI analysis")
        print("  python app.py serve                          # Web UI (post via the UI button)")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "hello":
        asyncio.run(hello_world())
    elif cmd == "hello-stream":
        asyncio.run(hello_world_streaming())
    elif cmd == "serve":
        import uvicorn
        # reload=True picks up code changes on save. Pass the import string
        # form ("app:app") rather than the app object so reload can work.
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    elif cmd.startswith("https://"):
        owner, repo, num = parse_github_url(cmd)
        asyncio.run(analyse_cli(owner, repo, num))
    elif len(sys.argv) == 4:
        asyncio.run(analyse_cli(sys.argv[1], sys.argv[2], int(sys.argv[3])))
    else:
        print("Error: Invalid arguments. Run without args for usage.")
        sys.exit(1)

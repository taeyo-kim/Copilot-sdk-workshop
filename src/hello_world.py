import asyncio
import os

from dotenv import load_dotenv
from copilot import CopilotClient
from copilot.session import PermissionHandler

load_dotenv()


async def main():
    # Create and start client
    client = CopilotClient()
    await client.start()

    # Create a session
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    session = await client.create_session(
        model="gpt-5",
        on_permission_request=PermissionHandler.approve_all,
        github_token=token,
    )

    # Wait for response using session.idle event
    done = asyncio.Event()

    def on_event(event):
        if event.type.value == "assistant.message":
            print(event.data.content)
        elif event.type.value == "session.idle":
            done.set()

    session.on(on_event)

    # Send a message and wait for completion
    await session.send("What is 2+2?")
    await done.wait()

    # Clean up
    await session.disconnect()
    await client.stop()

asyncio.run(main())
import asyncio
import websockets
import json

# Paste a fresh access token from any recent /login or /register response
ACCESS_TOKEN = "paste_your_access_token_here"
async def test_chat_stream():
    uri = f"ws://localhost:8000/api/v1/chat/stream?token={ACCESS_TOKEN}"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as ws:
            print("Connected successfully!")

            # Test 1: send a message, get echo back
            await ws.send("Hello from WebSocket test!")
            response = await ws.recv()
            print(f"Test 1 - Echo response: {response}")

            # Test 2: send another message
            await ws.send("Second message test")
            response = await ws.recv()
            print(f"Test 2 - Echo response: {response}")

            print("\nWebSocket test passed!")

    except Exception as e:
        print(f"WebSocket test failed: {e}")


async def test_invalid_token():
    """Confirm that an invalid token gets rejected."""
    uri = "ws://localhost:8000/api/v1/chat/stream?token=invalid_token_here"
    print("\nTesting invalid token rejection...")

    try:
        async with websockets.connect(uri) as ws:
            msg = await ws.recv()
            print(f"Unexpected connection: {msg}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Correctly rejected invalid token: connection closed with code {e.code}")
    except Exception as e:
        print(f"Rejected with: {e}")


asyncio.run(test_chat_stream())
asyncio.run(test_invalid_token())
"""Test MCP session management"""
import asyncio
import httpx
import json


async def test():
    mcp_url = "http://127.0.0.1:3845/mcp"
    headers = {"Accept": "application/json, text/event-stream"}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Initialize
        print("1. Initialize...")
        response = await client.post(
            mcp_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "ats", "version": "1.0.0"}
                }
            },
            headers=headers
        )
        print(f"   Status: {response.status_code}\n")
        
        # Send initialized notification
        print("2. Send initialized notification...")
        response = await client.post(
            mcp_url,
            json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            },
            headers=headers
        )
        print(f"   Status: {response.status_code}\n")
        
        # Now try resources/list
        print("3. List resources...")
        response = await client.post(
            mcp_url,
            json={"jsonrpc": "2.0", "id": 2, "method": "resources/list", "params": {}},
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}")


if __name__ == "__main__":
    asyncio.run(test())

# rec.py
from fastapi import FastAPI, Request
import uvicorn
import subprocess
import os

app = FastAPI()

connected = False
current_directory = os.getcwd()

@app.post("/connect")
async def connect(request: Request):
    global connected
    data = await request.json()
    command = data.get("command")

    if command == "connect":
        connected = True
        print("Received command: CONNECT")
        return {"status": "Connected!", "current_directory": current_directory}
    elif command == "disconnect":
        connected = False
        print("Received command: DISCONNECT")
        return {"status": "Disconnected!"}
    else:
        print(f"Received unknown command: {command}")
        return {"status": "Unknown command"}

@app.post("/command")
async def execute_command(request: Request):
    global current_directory
    if not connected:
        return {"status": "Not connected"}

    data = await request.json()
    command = data.get("command")

    print(f"Received command to execute: {command}")

    try:
        cmd = command.strip()

        if cmd.lower().startswith("go "):
            path = cmd[3:].strip().replace("/", "\\")
            if os.path.isdir(path):
                current_directory = os.path.abspath(path)
                return {"output": f"Changed directory to {current_directory}", "current_directory": current_directory}
            else:
                return {"output": f"Directory does not exist: {path}", "current_directory": current_directory}

        elif cmd.lower() == "help":
            help_text = (
                "Available Commands:\n"
                "-------------------------\n"
                "go <path>   - Change directory to specified path\n"
                "help        - Show this help message\n"
            )
            return {"output": help_text, "current_directory": current_directory}

        else:
            return {"output": "Unknown command. Use 'help' to see available commands.", "current_directory": current_directory}

    except Exception as e:
        return {"error": str(e), "current_directory": current_directory}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, Request
import uvicorn
import subprocess

app = FastAPI()

connected = False

@app.post("/connect")
async def connect(request: Request):
    global connected
    data = await request.json()
    command = data.get("command")
    
    if command == "connect":
        connected = True
        print("Received command: CONNECT")
        return {"status": "Connected!"}
    elif command == "disconnect":
        connected = False
        print("Received command: DISCONNECT")
        return {"status": "Disconnected!"}
    else:
        print(f"Received unknown command: {command}")
        return {"status": "Unknown command"}

@app.post("/command")
async def execute_command(request: Request):
    if not connected:
        return {"status": "Not connected"}

    data = await request.json()
    command = data.get("command")

    print(f"Received command to execute: {command}")
    
    try:
        # Execute the command and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        return {"output": output}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

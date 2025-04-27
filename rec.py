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

        elif cmd.lower().startswith("make folder "):
            folder_name = cmd[12:].strip()
            folder_path = os.path.join(current_directory, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            return {"output": f"Folder '{folder_name}' created at {current_directory}", "current_directory": current_directory}

        elif cmd.lower().startswith("make file "):
            file_name = cmd[10:].strip()
            file_path = os.path.join(current_directory, file_name)
            with open(file_path, 'w') as f:
                pass
            return {"output": f"File '{file_name}' created at {current_directory}", "current_directory": current_directory}

        elif cmd.lower() == "call":
            items = os.listdir(current_directory)
            details = []
            for item in items:
                item_path = os.path.join(current_directory, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    ext = os.path.splitext(item)[1][1:] or "No Extension"
                    details.append(f"{item} - Type=File, Extension={ext}, Size={size} bytes")
                elif os.path.isdir(item_path):
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(item_path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if os.path.isfile(fp):
                                total_size += os.path.getsize(fp)
                    details.append(f"{item} - Type=Folder, Size={total_size} bytes")
            output = "\n".join(details) if details else "No files or folders found."
            return {"output": output, "current_directory": current_directory}

        elif cmd.lower().startswith("remove folder "):
            folder_name = cmd[14:].strip()
            folder_path = os.path.join(current_directory, folder_name)
            if os.path.isdir(folder_path):
                import shutil
                shutil.rmtree(folder_path)
                return {"output": f"Folder '{folder_name}' has been deleted.", "current_directory": current_directory}
            else:
                return {"output": f"Folder '{folder_name}' does not exist.", "current_directory": current_directory}

        elif cmd.lower().startswith("remove file "):
            file_name = cmd[12:].strip()
            file_path = os.path.join(current_directory, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                return {"output": f"File '{file_name}' has been deleted.", "current_directory": current_directory}
            else:
                return {"output": f"File '{file_name}' does not exist.", "current_directory": current_directory}

        elif cmd.lower() == "help":
            help_text = (
                "Available Commands:\n"
                "-------------------------\n"
                "go <path>            - Change directory to specified path\n"
                "make folder <name>   - Create a new folder in current directory\n"
                "make file <name>     - Create a new empty file in current directory\n"
                "remove folder <name> - Delete a folder in current directory\n"
                "remove file <name>   - Delete a file in current directory\n"
                "call                 - List all files and folders with details\n"
                "help                 - Show this help message\n"
            )
            return {"output": help_text, "current_directory": current_directory}

        else:
            return {"output": "Unknown command. Use 'help' to see available commands.", "current_directory": current_directory}

    except Exception as e:
        return {"error": str(e), "current_directory": current_directory}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import os
import requests
import logging
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

LOCAL_WEBHOOKS = ["TERMINAL", "FILE"]

def webhook(integration: str, action: str, args: dict, webhook: str):
    """
    Args:
        integration: the extension to integrate with (i.e. notion)
        action: the action to perform (i.e. create)
        args: the information for the webhook (i.e. {page_name: ..., page_content: ...})
        webhook: the env variable for the webhook (i.e. {NOTION_N8N_WEBHOOK})
    """
    if webhook in LOCAL_WEBHOOKS:
        return local_webhook(integration, action, args, webhook)
    try:
        payload = {
            "integration": integration,
            "action": action,
            "args": args,
        }
        url = os.getenv(webhook)
        response = requests.post(url, json=payload, timeout=30)
        logging.info(payload)
        logging.info(response)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"webhook error: {payload}: {e}")
        return None

def local_webhook(integration: str, action: str, args: dict, webhook: str):
    """
    Same as webhook() but for local integrations
    """
    try:
        logging.info(f"Processing local webhook: {integration}.{action} with args: {args}")
        
        if webhook == "TERMINAL":
            return process_terminal(action, args)
        elif webhook == "FILES":
            return process_file(action, args)
        else:
            return {"error": f"Unknown local webhook: {webhook}"}
            
    except Exception as e:
        logging.error(f"Local webhook error: {integration}.{action}: {e}")
        return {"error": str(e)}

def process_file(action: str, args: dict):
    """
    Handle file operations: modify, open
    """
    if action == "modify":
        filepath = args.get("filepath")
        content = args.get("content", "")
        
        if not filepath:
            return {"error": "filepath is required"}
        
        try:
            # Create parent directories if they don't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logging.info(f"Successfully wrote {len(content)} characters to {filepath}")
            return {
                "success": True,
                "filepath": filepath,
                "message": f"File {filepath} created/modified successfully"
            }
            
        except Exception as e:
            return {"error": f"Failed to write file {filepath}: {str(e)}"}
    
    elif action == "open":
        filepath = args.get("filepath")
        
        if not filepath:
            return {"error": "filepath is required"}
        
        if not os.path.exists(filepath):
            return {"error": f"File {filepath} does not exist"}
        
        try:
            # Open file in VSCode
            subprocess.run(['code', filepath], check=True)
            
            logging.info(f"Successfully opened {filepath} in VSCode")
            return {
                "success": True,
                "filepath": filepath,
                "message": f"File {filepath} opened in VSCode"
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to open {filepath} in VSCode: {str(e)}"}
        except FileNotFoundError:
            return {"error": "VSCode (code command) not found. Make sure VSCode is installed and added to PATH"}
    
    else:
        return {"error": f"Unknown file action: {action}"}

def process_terminal(action: str, args: dict):
    """
    Handle terminal command execution
    """
    if action == "execute":
        command = args.get("command")
        working_dir = args.get("working_dir", ".")
        
        if not command:
            return {"error": "command is required"}
        
        # Validate working directory
        if not os.path.exists(working_dir):
            try:
                os.makedirs(working_dir, exist_ok=True)
                logging.info(f"Created working directory: {working_dir}")
            except Exception as e:
                return {"error": f"Failed to create working directory {working_dir}: {str(e)}"}
        
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            success = result.returncode == 0
            
            response = {
                "success": success,
                "command": command,
                "working_dir": working_dir,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if success:
                logging.info(f"Command executed successfully: {command}")
            else:
                logging.warning(f"Command failed with return code {result.returncode}: {command}")
                logging.warning(f"stderr: {result.stderr}")
            
            return response
            
        except subprocess.TimeoutExpired:
            return {
                "error": "Command timed out after 60 seconds",
                "command": command,
                "working_dir": working_dir
            }
        except Exception as e:
            return {
                "error": f"Failed to execute command: {str(e)}",
                "command": command,
                "working_dir": working_dir
            }
    
    else:
        return {"error": f"Unknown terminal action: {action}"}

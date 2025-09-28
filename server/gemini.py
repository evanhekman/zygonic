

from action import Action
from google import generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

class Model:
    def __init__(self):
        GEMINI_API_KEY = os.getenv
        with open("server/backbone.txt") as f:
            SYS_INSTR = f.read()
        with open("server/actions.json") as f:
            SYS_INSTR += f.read()
        
        if not SYS_INSTR:
            raise Exception("where yo prompt at")
        if not GEMINI_API_KEY:
            raise Exception("where yo key at")
        
        try:
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=SYS_INSTR
            )
            assert(self.model)

        except Exception as e:
            raise Exception(f"Error during model configuration: {e}")

    def query_action(self, q: str) -> dict:
        resp = self.model.generate_content(q)
        resp = resp.text
        assert(resp)
        if resp.startswith("```json"):
            resp = resp.strip("```json\n").strip("`")
        return json.loads(resp)

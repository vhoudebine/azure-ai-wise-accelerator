import os
from aiohttp import web
import json

class AppConfig:
    """AppConfig class to manage application configuration."""
    def __init__(self):
        pass

    @staticmethod
    async def get_personas(request):
            """Get personas profiles the user selects from."""
            personas_def_path = os.path.join(os.path.dirname(__file__), "util/personas.json")
            with open(personas_def_path, 'r') as f:
                personas_def_dict = json.load(f)
            return web.json_response(personas_def_dict)
    
    async def set_persona(self, request):
        """Set the current persona to be used in the app."""
        data = await request.json()
        persona_id = data.get("persona_id")
        personas_def_path = os.path.join(os.path.dirname(__file__), "util/personas.json")
        with open(personas_def_path, 'r') as f:
            personas_def_dict = json.load(f)
        
        # Check if the provided persona_id is valid
        persona = next((p for p in personas_def_dict['personas'] if p['id'] == persona_id), None)
        if not persona:
            return web.json_response({"error": "Invalid persona_id"}, status=400)
        # Check if the persona_id is provided
        if not persona_id:
            return web.json_response({"error": "No persona_id provided"}, status=400)

        # Store the persona in the shared app state
        self.app["current_persona"] = persona
        return web.json_response({"status": "Persona set", "persona": persona})
    
    def attach_to_app(self, app, path_prefix="/config"):
        """Attach routes to aiohttp app."""
        self.app = app
        app.router.add_get(f"{path_prefix}/get-personas", self.get_personas)
        app.router.add_post(f"{path_prefix}/set-persona", self.set_persona)

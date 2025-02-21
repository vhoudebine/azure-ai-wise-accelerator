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
    
    def attach_to_app(self, app, path_prefix="/config"):
        """Attach routes to aiohttp app."""
        app.router.add_get(f"{path_prefix}/get-personas", self.get_personas)
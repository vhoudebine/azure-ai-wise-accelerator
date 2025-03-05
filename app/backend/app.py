import logging
import os
from pathlib import Path

from aiohttp import web
import aiohttp_cors
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from tools import attach_tools_rtmt
from rtmt import RTMiddleTier
from evaluation import Evaluation
from app_config import AppConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

# Load environment variables from .env file
load_dotenv()

# Create the web application
async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()
    llm_endpoint = os.environ.get("AZURE_OPENAI_EASTUS2_ENDPOINT")
    llm_deployment = os.environ.get("AZURE_OPENAI_REALTIME_DEPLOYMENT")
    llm_key = os.environ.get("AZURE_OPENAI_EASTUS2_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    config = AppConfig()
    config.attach_to_app(app, "/config")

    # Enable CORS
    cors = aiohttp_cors.setup(app, defaults={
        "http://localhost:8766": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        ),
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=llm_endpoint,
        deployment=llm_deployment,
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy",
        app=app
    )
    rtmt.temperature = 0.6

    system_message = """
        You are Assistant that helps train Fiancial Advisors by role playing as a customer.
        When conversation starts, you are a customer who is looking to invest in a mutual fund.
        Start by introducing yourself and saying "I am looking to invest in a mutual fund."

        Your role is to be a customer who is looking to invest in a mutual fund.

        You should only use the information from the provided persona in order to answer the questions.
    """

    rtmt.system_message = system_message 

    # attach_tools_rtmt(rtmt,
    #     credentials=search_credential,
    #     search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
    #     search_index=os.environ.get("AZURE_SEARCH_INDEX"),
    #     semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or "default",
    #     identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
    #     content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
    #     embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
    #     title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
    #     use_vector_query=(os.environ.get("AZURE_SEARCH_USE_VECTOR_QUERY") == "true") or True
    # )

    rtmt.attach_to_app(app, "/realtime")

    # azurespeech = AzureSpeech(system_message=rtmt.system_message)
    # azurespeech.attach_to_app(app, "/azurespeech")
    eval = Evaluation()
    eval.attach_to_app(app, "/evaluation")

    # current_directory = Path(__file__).parent
    # app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    # app.router.add_static('/', path=current_directory / 'static', name='static')
    # app.router.add_static('/images', path=current_directory / 'images', name='images')  # Commented out
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)

    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)

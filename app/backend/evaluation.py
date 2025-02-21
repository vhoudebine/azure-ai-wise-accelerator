import os
import json
import logging
from aiohttp import web
from openai import AzureOpenAI
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from wise.fact_checker import FactChecker
from wise.fact_extractor import FactExtractor
from wise.evaluator import Evaluator

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv(override=True)

class Evaluation:
    def __init__(self):
        # Azure OpenAI Client
        self.aoai_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_EASTUS_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_EASTUS_API_KEY"),
        )

        # create Azure Storage Container Client to download the source documents
        # storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        storage_container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        blob_service_client = BlobServiceClient(
             account_url=f"https://{storage_account_name}.blob.core.windows.net",
             credential=DefaultAzureCredential()
         )
        #blob_service_client = BlobServiceClient.from_connection_string(storage_connect_str)
        self.container_client = blob_service_client.get_container_client(storage_container_name)

        # create Azure Document Intelligence Client to parse the PDF documents
        doc_intelligence_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        doc_intelligence_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

        print(doc_intelligence_endpoint
              )
        print(doc_intelligence_key)
        self.document_analysis_client = DocumentIntelligenceClient(
            endpoint=doc_intelligence_endpoint,
            credential=AzureKeyCredential(doc_intelligence_key)
        )
    
    async def get_avatar(self, request):
        """Get avatar profiles the user selects from."""
        avatar_def_path = os.path.join(os.path.dirname(__file__), "util/avatars.json")

        avatar_def_dict = json.loads(avatar_def_path)
        return web.json_response(avatar_def_dict)

    async def generate_response(self, request):
        """Generate AI response using Azure OpenAI GPT."""
        logging.info(f"running generate_response")
        # testin

        response = self.aoai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "you are a helpful assistant"},
                {"role": "user", "content": "hello"},
            ],
            temperature=0.6,
        )
        print(response.choices[0].message.content)

        return web.json_response({"response": "doing some stuff"})

    async def upload_document(self, request):
        """Upload the document to Azure Blob Storage without saving locally."""
        logging.info(f"running upload_document")
        try:
            reader = await request.multipart()
            document_part = await reader.next()
            document_name = document_part.filename
            print(document_name)
            # Read the entire file instead of looping through chunks
            data = await document_part.read()
            # Ensure data is bytes
            if not isinstance(data, bytes):
                data = str(data).encode("utf-8")
            # saving to blob storage
            blob_client = self.container_client.get_blob_client(blob=document_name)
            blob_client.upload_blob(data, overwrite=True)

            logging.info(f"Document '{document_name}' uploaded to blob storage successfully.")
            return web.json_response({"message": "Document uploaded successfully."})
        except Exception as e:
            logging.error(f"Document upload failed: {e}")
            return web.json_response({"error": "Internal server error."}, status=500)
        
    async def gerenate_facts(self, request):
        """using the blob storage to generate facts"""
        logging.info(f"running generate_facts")
        try:
            # get request and check if overwriting the facts file flag is set
            data = await request.json()
            overwrite = data.get("overwrite", False)

            # check if facts file already exists
            fact_file = os.path.join(os.path.dirname(__file__), "util/facts.txt")
            if os.path.exists(fact_file) and not overwrite:
                logging.info(f"Facts file already exists.")
                return web.json_response({"message": "Facts file already exists."})

            extractor = FactExtractor(
                aoai_client=self.aoai_client,
                document_analysis_client=self.document_analysis_client, 
                storage_container_client=self.container_client
            )

            facts = extractor.extract_facts()
            # save fact file to util folder as facts.txt
            with open(fact_file, "w", encoding="utf-8") as f:
                f.write("\n".join(facts))

            logging.info(f"Document analysis completed successfully.")
            return web.json_response({"message": "Facts generated successfully."})
        except Exception as e:
            logging.error(f"Document analysis failed: {e}")
            return web.json_response({"error": "Internal server error."}, status=500)

    async def fact_check(self, request):
        """Fact check the user's input."""

        # check if util folder has facts.txt file
        fact_file = os.path.join(os.path.dirname(__file__), "util/facts.txt")
        if not os.path.exists(fact_file):
            return web.json_response({"error": "Facts file not found."}, status=500)
        
        # read the facts from the file
        with open(fact_file, "r") as f:
            facts = f.read().splitlines()

        try:
            data = await request.json()
            transcript = data.get("transcript")

            fact_string = ('##### \n').join(facts)
            fact_checker = FactChecker(self.aoai_client, fact_string, model='gpt-4o-global')
            fact_checker_report = fact_checker.check_transcript(transcript)
            return web.json_response(fact_checker_report)
        except Exception as e:
            logging.error(f"Text-to-speech failed: {e}")
            return web.json_response({"error": "Internal server error."}, status=500)


    async def transcript_evaluate(self, request):
        """Evaluate the transcript based on the evaluation criteria."""
        data = await request.json()
        transcript = data.get("transcript")
        
        evaluation_criteria = [
            {   
                "criteria":"Next_steps",
                "description":"The Advisor planned clear next steps for the Client to take after the conversation.",
                "score":1
            },  
            {   
                "criteria":"Product_knowledge",
                "description": "The Advisor demonstrated a strong understanding of the products they were discussing.",
                "score":1
            },
            {
                "criteria": "Discovery",
                "description":" The Advisor asked the Client questions to understand their needs and preferences.",
                "score":1
            }
        ]

        theme = "Initial call between a wealth advisor and a prospective customer"

        evaluator = Evaluator(self.aoai_client, evaluation_criteria, theme)
        evaluation = evaluator.evaluate_transcription(transcript)

        print(evaluation)
        return web.json_response(evaluation)



    def attach_to_app(self, app, path_prefix="/evaluation"):
        """Attach routes to aiohttp app."""
        app.router.add_post(f"{path_prefix}/generate-response", self.generate_response)
        app.router.add_post(f"{path_prefix}/gerenate-facts", self.gerenate_facts)
        app.router.add_post(f"{path_prefix}/upload-document", self.upload_document)
        app.router.add_post(f"{path_prefix}/fact-check", self.fact_check)
        app.router.add_post(f"{path_prefix}/transcript-evaluate", self.transcript_evaluate)

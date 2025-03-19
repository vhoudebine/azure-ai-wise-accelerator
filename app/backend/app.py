import logging
import os
from pathlib import Path

from aiohttp import web
import aiohttp_cors
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

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
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "ballad",
        app=app
    )
    rtmt.temperature = 0.6


    system_message = """
    You are AI Assistant, designed to helps train Financial Advisors at Fidelity by way of simulation.
    This is a role playing exercise designed to help Financial Advisors practice their sales skills by putting them in front of AI assistant who is acting a virtual prospect.
    In this exercise, you are an AI Assistant, you are a prospective customer who the user, a Fidelity Fiancial Advisor, is trying to sell a Fidelity product to.
    You, the AI Assistant, are not a financial advisor, you are not an expert in finance and you will ask questions about the products.
    The user, who is a financial advisor, will start off by introducing themselves and asking you, the AI Assistant, some questions about yourself.
    You, the AI Assistant, will respond to the user's questions as if you were a real potential customer.
    The user's goal is to get you, AI Assistant, to say yes to an investment.
    Your goal to make sure that the investment is good for you and your family.
    If after all your questions have been answered, you, the AI Assistant, are still not ready to invest, you, the AI Assistant can say "I need to think about it" or "I need to talk to my spouse" or "I need to talk to my financial advisor" or "I need to do more research".
    If the financial advisor is too pushy and you are not interested, you can say good bye and end the conversation.
    You can also ask about the financial advisor's background and experience.
    Ask questions about the products and ask for clarification if you anything is unclear.
    
    Some example questions you can ask are:
    
    What is the fund's investment objective? - Understand the primary goal of the fund, whether it's growth, income, or a combination of both.
    What is the fund's historical performance? - Review the fund's past performance over different time periods (1 year, 5 years, 10 years) to gauge its consistency and resilience.
    What are the fees and expenses associated with the fund? - Look into the expense ratio, management fees, and any other costs that might affect your returns.
    What is the fund's risk level? - Assess the fund's risk profile and determine if it aligns with your risk tolerance.
    Who is the fund manager and what is their track record? - Understand the experience and performance history of the fund manager(s) to ensure they have a successful track record.
    What is the fund's investment strategy? - Understand the strategies and methodologies the fund uses to achieve its objectives, including asset allocation and sector focus.
    What are the fund's holdings? - Review the types of securities the fund invests in and their proportions to ensure they align with your investment goals.
    What is the fund's turnover rate? - A high turnover rate can indicate frequent trading, which might lead to higher transaction costs and tax implications.
    Are there any restrictions or lock-in periods? - Check if there are any restrictions on when you can sell your shares or if there are any penalties for early withdrawal.
    How does the fund compare to its benchmark? - Compare the fund's performance to a relevant benchmark index to see how well it has performed relative to the market.

    You, as the AI Assistant, can also ask any other relevant question.

    Challenge the financial advisor if they are not able to answer your questions.

    More information about you, as the AI Assistant acting as the proscpective customer:
    - You are acting as John.
    - John is 35 years old.
    - John is married with two children.
    - John is a software engineer.
    - John is looking to invest for his children's education.
    - John is looking for a fund that is low risk and has a good return.
    - John is looking to invest $10,000 but do not tell the advisor this amount right away. They will ask you how much you want to invest. Be coy about it until they've built some rapport with you.
    - John is looking to invest for 5 years.
    - John is a skeptic with a cynical personality
    - John is not an expert in finance and you will ask questions about the products.
    - John is currenly invested in a 401k and a Roth IRA.
    - John is not interested in crypto or NFTs.
    - John is not interested in day trading or short term investments.
    - John is not interested in penny stocks or high risk investments.
    - John is not interested in real estate or rental properties.
    - John may be interested in bonds or fixed income investments.
    - John may be interested in ETFs or index funds.
    - John may be interested in mutual funds or target date funds.
    - John may be interested in socially responsible investing or ESG funds.
    - John may be interested in robo-advisors or automated investing.
    - John may be interested in tax-advantaged accounts or tax-efficient investing.
    - John may be interested in retirement accounts or retirement planning.
    - John may be interested in college savings accounts or 529 plans.
    - John may be interested in health savings accounts or HSAs.


    Give the advisor a hard time and make them work for the sale. As they asnwer your questions to your satisfaction, you can start to warm up to them and be more agreeable.
    If John is not interested in the product, you can say "I need to think about it" or "I need to talk to my spouse" or "I need to talk to my financial advisor" or "I need to do more research".
    Ultimately, based on the information about John, and based on the financial products positioned to him, if you see a good fit, you can say "I am interested in this product" or "I would like to invest in this product" or "I would like to learn more about this product" or "I would like to schedule a follow up meeting with you to discuss this product further".
    If John is not interested in the product, you can say "I need to think about it" or "I need to talk to my spouse" or "I need to talk to my financial advisor" or "I need to do more research".
    You need to gather all the data points from the advisor and then make a decision while challenging the advisor on their responses.
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

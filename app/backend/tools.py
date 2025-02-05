from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection


""""
Purpose of the Tool:
    Knowledge Base Search:
        Enable GPT-4o to search the knowledge base for information on beverages, including categories, names, descriptions, origins, caffeine content, brewing methods, popularity, and sizes.
    User Interaction:
        Provide users with detailed information about beverages, including categories, names, descriptions, origins, caffeine content, brewing methods, popularity, and sizes.
    Error Prevention:
        Prevent hallucination by ensuring that all information provided to the user is sourced from the knowledge base.
"""
search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "Search the knowledge base. The knowledge base is in English, translate to and from English if " + \
                   "needed. Results are formatted as a source name first in square brackets, followed by the text " + \
                   "content, and a line with '-----' at the end of each result.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

async def search(
    search_client: SearchClient, 
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any) -> ToolResult:

    query = args['query']
    print(f"\nStarting search for '{query}' in the knowledge base.")
    
    # Hybrid + Reranking query using Azure AI Search
    vector_queries = []
    if use_vector_query:
        vector_queries.append(VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields=embedding_field))

    # Perform the hybrid search
    search_results = await search_client.search(
        search_text=query, 
        query_type="semantic",
        semantic_configuration_name=semantic_configuration,
        top=5,
        vector_queries=vector_queries,
        select=["id", "category", "name", "description", "longDescription", "origin", "caffeineContent", "brewingMethod", "popularity", "sizes"],
    )
    results = ""

    async for r in search_results:
        results += f"[{r['id']}]: Category: {r['category']}, Name: {r['name']}, Description: {r['description']}, Long Description: {r['longDescription']}, Origin: {r['origin']}, Caffeine Content: {r['caffeineContent']}, Brewing Method: {r['brewingMethod']}, Popularity: {r['popularity']}, Sizes: {r['sizes']}\n-----\n"
    print(f"Search results: {results}")
    return ToolResult(results, ToolResultDirection.TO_SERVER)


# Attach tools to the RTMiddleTier instance
def attach_tools_rtmt(rtmt: RTMiddleTier,
    credentials: AzureKeyCredential | DefaultAzureCredential,
    search_endpoint: str, search_index: str,
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    title_field: str,
    use_vector_query: bool
    ) -> None:

    if not isinstance(credentials, AzureKeyCredential):
        credentials.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    search_client = SearchClient(search_endpoint, search_index, credentials, user_agent="RTMiddleTier")

    rtmt.tools["search"] = Tool(schema=search_tool_schema, target=lambda args: search(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args))
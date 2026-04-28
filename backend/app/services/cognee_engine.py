import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
import cognee
from cognee.api.v1.search import SearchType
from cognee import recall as cognee_recall
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Cognee configuration
def setup_cognee():
    from cognee.base_config import get_base_config
    config = get_base_config()
    
    if settings.system_root_directory:
        config.system_root_directory = os.path.abspath(settings.system_root_directory)
    if settings.data_root_directory:
        config.data_root_directory = os.path.abspath(settings.data_root_directory)
        
    logger.info(f"Cognee System Root: {config.system_root_directory}")
    logger.info(f"Cognee Data Root: {config.data_root_directory}")
    
    # Update os.environ just in case as well
    os.environ["SYSTEM_ROOT_DIRECTORY"] = config.system_root_directory
    os.environ["DATA_ROOT_DIRECTORY"] = config.data_root_directory

setup_cognee()

async def ingest_document(file_path: str, dataset_name: str = "default"):
    """
    Ingest a document into Cognee using the V2 remember API.
    """
    try:
        logger.info(f"Remembering document in Cognee: {file_path} (dataset: {dataset_name})")
        # remember() handles both adding and processing (cognifying)
        await cognee.remember(file_path, dataset_name = dataset_name)
        return True
    except Exception as e:
        logger.error(f"Failed to ingest document into Cognee: {str(e)}")
        raise

async def get_knowledge_graph(query: str = None):
    """
    Retrieve or search the knowledge graph.
    If query is provided, performs a RAG search.
    Otherwise, can be used to visualize or list graph data.
    """
    try:
        if query:
            logger.info(f"Searching Cognee graph with query: {query}")
            results = await cognee.search(
                query_type = SearchType.RAG_COMPLETION,
                query_text = query
            )
            return results
        else:
            # Default to visualization or basic graph info if no query
            # Note: visualize_graph often opens a browser or returns a URL/path
            return await cognee.visualize_graph()
    except Exception as e:
        logger.error(f"Failed to retrieve Cognee knowledge graph: {str(e)}")
        return None

async def search_graph(query: str, search_type: SearchType = SearchType.RAG_COMPLETION):
    """
    Search the graph using Cognee.
    """
    try:
        results = await cognee.search(
            query_type = search_type,
            query_text = query
        )
        return results
    except Exception as e:
        logger.error(f"Cognee search failed: {str(e)}")
        return f"Search error: {str(e)}"

async def recall_context(query: str, datasets: List[str] = None):
    """
    Use Cognee's V2 recall API to find context.
    """
    try:
        logger.info(f"Recalling context for query: {query}")
        results = await cognee_recall(
            query_text = query,
            datasets = datasets
        )
        return results
    except Exception as e:
        logger.error(f"Cognee recall failed: {str(e)}")
        return []

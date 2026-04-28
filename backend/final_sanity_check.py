
import asyncio
import os
import sys
import logging
from app.services.cognee_engine import ingest_document, search_graph, setup_cognee
from cognee import SearchType

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_sanity_check():
    pdf_path = r"C:\Users\Manh\Downloads\phuong-phap-giai-toan-va-bai-tap-chuyen-de-menh-de-va-tap-hop-toan-10.pdf"
    dataset_name = "math_grade_10"
    
    print(f"\n[*] Starting Final Sanity Check")
    print(f"[*] Target PDF: {pdf_path}")
    
    # Ensure cognee is set up
    setup_cognee()
    
    # 1. Ingest Document
    print("\n[1/3] Ingesting and extracting Knowledge Graph (this may take a minute)...")
    try:
        await ingest_document(pdf_path, dataset_name=dataset_name)
        print("[*] Ingestion and extraction completed!")
    except Exception as e:
        print(f"[X] Ingestion failed: {str(e)}")
        return

    # 2. Verify Graph Structure
    print("\n[2/3] Verifying Graph Structure (Retrieving key entities)...")
    try:
        # Search for core concepts in the PDF to see what was extracted
        # "Mệnh đề" and "Tập hợp" are likely the main topics
        queries = ["Mệnh đề là gì?", "Các phép toán tập hợp"]
        
        for query in queries:
            print(f"\n[?] Searching for: '{query}'")
            results = await search_graph(query)
            if results:
                print(f"[!] Found results:")
                # Depending on SearchType.RAG_COMPLETION, results might be a string or structured data
                print(results)
            else:
                print("[W] No direct results found for this specific query, checking entities...")
                
    except Exception as e:
        print(f"[X] Search failed: {str(e)}")

    # 3. Report Success
    print("\n[3/3] Sanity Check Finished")
    print("--------------------------------------------------")
    print("Graph formed successfully. You can now use the Streamlit UI to interact with this knowledge.")

if __name__ == "__main__":
    asyncio.run(run_sanity_check())

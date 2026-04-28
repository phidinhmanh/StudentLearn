import asyncio
import cognee

async def list_top_nodes():
    try:
        # Use recall to find any mathematical entities
        results = await cognee.recall("Toán học")
        with open("graph_report.txt", "w", encoding="utf-8") as f:
            f.write("Extracted Entities (Knowledge Recall):\n")
            if results:
                f.write(f"{results}\n")
            else:
                f.write("No entities found in recall. The graph might be indexed differently.\n")
    except Exception as e:
        with open("graph_report.txt", "w", encoding="utf-8") as f:
            f.write(f"Error recalling nodes: {str(e)}")

if __name__ == "__main__":
    asyncio.run(list_top_nodes())

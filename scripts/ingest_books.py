import asyncio
import os
import logging
from pypdf import PdfReader
from opensearchpy.helpers import async_bulk

# Set up relative imports to reuse our core infrastructure
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.vector_store.client import os_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapped configurations for our three domain indices
TARGET_INDICES = ["ml_book", "dl_book", "mlops_book"]
CHUNK_SIZE = 1000 # Number of characters per text chunk

async def create_indices(client):
    """Initializes the OpenSearch indices if they do not already exist."""
    for index_name in TARGET_INDICES:
        exists = await client.indices.exists(index=index_name)
        if not exists:
            # Create a standard index mapped for text search
            await client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "content": {"type": "text"}
                        }
                    }
                }
            )
            logger.info(f"Created index: {index_name}")
        else:
            logger.info(f"Index {index_name} already exists. Skipping creation.")

def extract_and_chunk_pdf(file_path: str, title: str, index_name: str):
    """Reads a PDF and splits it into manageable overlapping chunks."""
    logger.info(f"Extracting text from: {file_path}")
    try:
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + " "
                
        # Basic fixed-size chunking (In production, use recursive character chunking)
        chunks = [full_text[i:i + CHUNK_SIZE] for i in range(0, len(full_text), CHUNK_SIZE)]
        logger.info(f"Generated {len(chunks)} chunks for {title}")
        
        # Format the chunks for OpenSearch Bulk API
        actions = []
        for i, chunk in enumerate(chunks):
            actions.append({
                "_op_type": "index",
                "_index": index_name,
                "_id": f"{title.replace(' ', '_')}_chunk_{i}",
                "_source": {
                    "title": title,
                    "content": chunk.encode("utf-8", "ignore").decode("utf-8").strip()
                }
            })
        return actions
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return []

async def main():
    logger.info("Starting ingestion pipeline...")
    
    client = os_manager.get_client()
    is_connected = await os_manager.check_health()
    if not is_connected:
        logger.error("Aborting ingestion. OpenSearch is unreachable.")
        return

    # 1. Prepare Database
    await create_indices(client)

    # 2. Extract and Transform
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
    all_actions = []
    
    # Mapping filenames to their respective indices
    # Ensure your PDFs in data/raw match these exact filenames
    file_mappings = {
        "Machine_Learning.pdf": "ml_book",
        "Deep_Learning.pdf": "dl_book",
        "MLOps_Guide.pdf": "mlops_book"
    }

    for filename, index_name in file_mappings.items():
        file_path = os.path.join(raw_dir, filename)
        if os.path.exists(file_path):
            actions = extract_and_chunk_pdf(file_path, title=filename.replace('.pdf', ''), index_name=index_name)
            all_actions.extend(actions)
        else:
            logger.warning(f"File not found: {file_path}. Please add it to data/raw/.")

    # 3. Load (Bulk Insert via asyncio)
    if all_actions:
        logger.info(f"Bulk inserting {len(all_actions)} total chunks into OpenSearch...")
        success, failed = await async_bulk(client, all_actions, raise_on_error=False)
        logger.info(f"Ingestion complete. Success: {success}, Failed: {len(failed)}")
    else:
        logger.warning("No data was extracted. Nothing to insert.")

    # Close the async connection safely
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
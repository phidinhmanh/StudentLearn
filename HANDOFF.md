# StudentLearn AI Project Handoff

Welcome to the newly optimized **StudentLearn AI** project. The backend has been completely migrated to a local-first architecture using **Cognee** and **Gemini**, replacing the legacy Neo4j requirements.

## 🚀 Key Changes
- **Local Knowledge Graph**: Powered by Kuzu DB. No external graph database installation required.
- **Gemini Integration**: Uses Google's native Gemini API for cost-effective and powerful extraction.
- **Hybrid Retrieval**: Search now uses semantic recall, making it more resilient to messy data.
- **Windows Optimized**: Resolved database file-locking issues by using absolute paths.

## 🛠️ Prerequisites
1. **Python 3.10+**: Ensure your virtual environment is active.
2. **Environment Variables**: Update `.env` with:
   - `GOOGLE_API_KEY`: Your Gemini API key.
   - `COGNEE_SYSTEM_PATH`: Full absolute path to the `.cognee_system` folder in your project.
   - `LLM_PROVIDER="gemini"`
   - `EMBEDDING_PROVIDER="gemini"`

## 🏁 Running the Application

### 1. Start the Backend (FastAPI)
Navigate to the `backend` directory and run:
```bash
uvicorn app.main:app --reload
```
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 2. Start the Streamlit UI
Open a new terminal, navigate to `backend`, and run:
```bash
streamlit run app/test_ui/Home.py
```
- **Dashboard**: View knowledge extraction progress.
- **GraphRAG**: Interact with your uploaded documents using the new hybrid search.

## 📂 Data Storage
- All graph data is stored locally in `.cognee_system/`.
- If you need to reset the database, simply delete the `.cognee_system` folder (ensure the backend is stopped first).

## 🧪 Maintenance
- **Updating Schema**: If you change the underlying data models, run `cognee.prune()` to refresh the local graph structure.
- **Logs**: Detailed logs are available in `C:\Users\Manh\.cognee\logs\`.

---
*Developed with ❤️ for the StudentLearn project.*

# StudentLearn Knowledge Graph Handoff

## 🚀 Ready to Launch (One-liner)
Copy and paste this into your PowerShell terminal (from the `backend` folder) to start Backend immediately:
```powershell
Start-Process -NoNewWindow .\.venv\Scripts\python.exe -ArgumentList "-m uvicorn app.main:app --reload --port 7000"
```

## 🚀 System Status
The Knowledge Graph extraction pipeline is now **STABLE** and optimized for **Gemma 4**.

### Core Configuration (.env in `backend/`)
- **LLM_PROVIDER**: `gemini`
- **LLM_MODEL**: `gemini/gemma-4-26b-a4b-it` (Native Google provider via LiteLLM)
- **EMBEDDING_PROVIDER**: `gemini`
- **GRAPH_DATABASE**: `kuzu`

## 🛠️ Key Scripts (in `backend/`)
- `final_demo.py`: Main entry point for ingesting documents.

## 📊 Recent Success
We successfully processed 3 pages of the Mathematics Grade 10 textbook:
- **Nodes Extracted**: 16 (including core concepts like `mệnh đề`, `tập hợp`, `số nguyên tố`)
- **Relationships**: Captured logical links between concepts.
- **Language Support**: Full Vietnamese support for entities and descriptions.

## ⚠️ Known Limitations
- **Rate Limits**: The Gemini free tier has a limit of 100 embedding requests per minute. Processing documents larger than 5-10 pages at once may trigger `429 Resource Exhausted`.
- **Workaround**: Break large documents into smaller chunks or use a paid tier API key.

## 📁 Database Locations
- **Cognee Metadata**: `backend/.cognee_system/databases/cognee_db` (SQLite)
- **Graph Data**: `backend/.cognee_system/databases/kuzu_db` (Kuzu)

## 🔄 Next Steps
1. **Frontend Integration**: Use the Android app to interact with the backend.
2. **Quiz Generation**: Use `cognee.recall()` with semantic search to pull nodes for the quiz generator.

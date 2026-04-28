# FastAPI Backend: LLM Calls Exploration Report

## Executive Summary

The StudentLearn backend makes LLM calls in 4 primary service files and 1 utility file. The calls are made through two different LLM providers:
- **OpenRouter/OpenAI-compatible API** (used via ChatOpenAI from langchain_openai)
- **Google Generative AI** (used via ChatGoogleGenerativeAI from langchain_google_genai)

There is NO existing retry or fallback logic for LLM calls at the infrastructure level, though some services have JSON parsing fallbacks.

## Key Findings

### 1. LLM Factory & Configuration
- **File:** app/utils/gemini_client.py
- **Factory Function:** get_llm(temperature: float = 0) -> ChatOpenAI
- **Configuration:** 
  - openrouter_model: "llama-3.3-70b-versatile"
  - openrouter_base_url: "https://api.groq.com/openai/v1"
  - Timeout: 120 seconds
  - API key fallback: openrouter -> gemini -> "test-key"

### 2. Services Making LLM Calls

#### Service 1: Quiz Generator
- File: app/services/quiz_generator.py
- Line 82: llm = get_llm(temperature=0.5)
- Line 83: response = await asyncio.to_thread(llm.invoke, prompt)
- Error Handling: JSON parsing fallback to hardcoded questions (lines 86-101)
- Entry Point: POST /quiz/{topic_id}

#### Service 2: Graph Extractor
- File: app/services/graph_extractor.py
- Line 126: llm = get_llm(temperature=0)
- Line 127: response = await asyncio.to_thread(llm.invoke, prompt)
- Batch Processing: 3 chunks per batch, asyncio.gather() for parallelization (lines 24-34)
- Error Handling: JSON parsing fallback to empty graph (lines 131-148)
- Entry Point: POST /documents/ingest

#### Service 3: Learning Path Engine
- File: app/services/learning_path_engine.py
- Line 114: llm = get_llm(temperature=0.3)
- Line 115: response = await asyncio.to_thread(llm.invoke, prompt)
- Error Handling: JSON parsing fallback to simple path (lines 119-132)
- Entry Points: GET /learning-path/{user_id}, POST /learning-path/generate

#### Service 4: Graph RAG Service
- File: app/services/graph_rag_service.py
- **IMPORTANT:** Uses ChatGoogleGenerativeAI directly (NOT get_llm factory)
- Line 23-27: synthesizer_llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash")
- Line 29-33: cypher_llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash")
- LLM Calls:
  - Line 169: graph_result = self.graph_cypher_chain.invoke({"query": question})
  - Line 207: final_response = self.synthesizer_llm.invoke(prompt)
  - Line 218: response = self.agent_with_history.invoke(...)
- Error Handling: Generic exception handling with error messages (no retry)

### 3. LLM Call Summary Table

| Service | File | Function | Method | Temp | Line | Retry |
|---------|------|----------|--------|------|------|--------|
| Quiz Generator | quiz_generator.py | generate_quiz | llm.invoke | 0.5 | 83 | JSON fallback |
| Graph Extractor | graph_extractor.py | _extract_from_batch | llm.invoke | 0 | 127 | JSON fallback |
| Learning Path | learning_path_engine.py | generate_learning_path | llm.invoke | 0.3 | 115 | JSON fallback |
| GraphRAG | graph_rag_service.py | hybrid_rag_runner | synthesizer_llm.invoke | 0 | 207 | Error only |
| GraphRAG | graph_rag_service.py | hybrid_rag_runner | cypher_chain.invoke | 0 | 169 | Error only |

### 4. API Flow Diagrams

**Quiz Flow:**
`
POST /quiz/{topic_id}
  -> app/routers/quiz.py:43-50 (get_quiz)
     -> app/services/quiz_generator.py:9-111 (generate_quiz)
        -> [LLM CALL] line 83: llm.invoke(prompt)
`

**Document Ingestion Flow:**
`
POST /documents/ingest
  -> app/routers/documents.py:31-85 (ingest_document)
     -> app/services/graph_extractor.py:12-84 (extract_knowledge_graph)
        -> app/services/graph_extractor.py:87-149 (_extract_from_batch) [BATCHED x N]
           -> [LLM CALL] line 127: llm.invoke(prompt) [PARALLEL]
`

**Learning Path Flow:**
`
GET /learning-path/{user_id}
  -> app/routers/learning_path.py:26-40 (get_learning_path)
     -> app/services/learning_path_engine.py:8-21 (get_personalized_path)
        -> [CACHED] OR app/services/learning_path_engine.py:24-137 (generate_learning_path)
           -> [LLM CALL] line 115: llm.invoke(prompt)
`

**GraphRAG Flow:**
`
POST /graph-rag/query
  -> app/routers/graph_rag.py (query endpoint)
     -> app/services/graph_rag_service.py:217-222 (query)
        -> app/services/graph_rag_service.py:61-66 (agent_with_history.invoke)
           -> app/services/graph_rag_service.py:161-210 (hybrid_rag_runner)
              -> [LLM CALL] line 169: graph_cypher_chain.invoke({"query": question})
              -> [LLM CALL] line 207: synthesizer_llm.invoke(prompt)
`

### 5. Error Handling Analysis

**Current State:**
- No retry logic at LLM call level
- JSON parsing fallbacks in Quiz, Graph Extractor, Learning Path
- Graph Extractor silent failure (empty graph on JSON error)
- GraphRAG error messages only

**Missing:**
- No exponential backoff decorator
- No provider fallback
- No circuit breaker
- No request deduplication

### 6. Batch Processing & Concurrency

**Graph Extractor Batching (lines 24-34):**
- Batch size: 3 chunks
- Method: asyncio.gather(*tasks) for parallel execution
- Each batch calls get_llm() independently
- Opportunity for round-robin distribution

### 7. Files to Modify for Round-Robin Implementation

1. app/utils/gemini_client.py - Central factory enhancement
2. app/config.py - Provider list configuration
3. app/services/quiz_generator.py - Add retry decorator
4. app/services/graph_extractor.py - Add retry decorator
5. app/services/learning_path_engine.py - Add retry decorator
6. app/services/graph_rag_service.py - Special handling for GraphRAG

### 8. Summary Statistics

| Metric | Count |
|--------|-------|
| Total LLM Call Sites | 5 |
| Services Making LLM Calls | 4 |
| API Routes | 5 |
| Parallel Batch Operations | 1 (Graph Extractor) |
| Retry/Fallback Mechanisms | JSON parsing only |
| Direct Provider Instantiations | 2 (GraphRAG) |
| Factory Function Usages | 3 |
| Async LLM Calls | 5/5 (all use asyncio.to_thread) |
| Timeout Configuration | 120 seconds |

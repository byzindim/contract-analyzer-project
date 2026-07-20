
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import httpx
import faiss
import json
import numpy as np
import time
import os

# ==========================================
# 1. НАСТРОЙКИ И ПУТИ
# ==========================================
PROJECT_ROOT = '/content/drive/MyDrive/contract-analyzer-project'
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, 'rag_artifacts')

# Глобальные объекты
faiss_index = None
metadata_mapping = None
ollama_client = None

# ==========================================
# 2. LIFESPAN (Решение проблемы Cold Start)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global faiss_index, metadata_mapping, ollama_client
    print("🚀 [LIFESPAN] Запуск API...")
    
    # Загрузка FAISS
    print("📥 [LIFESPAN] Загрузка FAISS индекса в RAM...")
    faiss_index = faiss.read_index(os.path.join(ARTIFACTS_DIR, 'faiss_index.index'))
    with open(os.path.join(ARTIFACTS_DIR, 'metadata_mapping.json'), 'r', encoding='utf-8') as f:
        metadata_mapping = json.load(f)
    print(f"✅ [LIFESPAN] FAISS загружен: {faiss_index.ntotal} векторов")
    
    # Инициализация клиента
    ollama_client = httpx.AsyncClient(timeout=60.0)
    
    # 🔥 WARM-UP (Прогрев Ollama)
    print("🔥 [LIFESPAN] Прогрев Ollama (загрузка моделей в VRAM)...")
    try:
        await ollama_client.post("http://localhost:11434/api/embed", json={"model": "bge-m3", "input": "warmup"})
        await ollama_client.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:7b", "prompt": "warmup", "stream": False})
        print("✅ [LIFESPAN] Ollama прогрета! Первый пользователь не будет ждать.")
    except Exception as e:
        print(f"⚠️ [LIFESPAN] Ошибка прогрева: {e}")
        
    yield  
    
    print("🛑 [LIFESPAN] Остановка API...")
    await ollama_client.aclose()

# ==========================================
# 3. ИНИЦИАЛИЗАЦИЯ FASTAPI
# ==========================================
app = FastAPI(
    title="Contract Analyzer RAG API",
    description="API для анализа юридических договоров ООО 'ФЛАЙ-НСК'",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==========================================
# 4. PYDANTIC DTO (Схемы данных)
# ==========================================
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="Вопрос юриста")
    top_k: int = Field(default=5, ge=1, le=20, description="Количество чанков для поиска")

class SourceCitation(BaseModel):
    file: str
    page: int
    counterparty: str
    doc_type: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]

# ==========================================
# 5. БИЗНЕС-ЛОГИКА (RAG ПАЙПЛАЙН)
# ==========================================
async def get_embedding(text: str) -> list[float]:
    response = await ollama_client.post("http://localhost:11434/api/embed", json={"model": "bge-m3", "input": text})
    response.raise_for_status()
    return response.json()["embeddings"][0]

def retrieve_context(query_vector: np.ndarray, top_k: int) -> list[dict]:
    distances, indices = faiss_index.search(query_vector, top_k)
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            chunk_data = metadata_mapping.get(str(idx), {})
            results.append({
                "rank": i + 1,
                "score": float(distances[0][i]),
                "text": chunk_data.get("text", ""),
                "metadata": chunk_data.get("metadata", {})
            })
    return results

def format_context_for_llm(chunks: list[dict]) -> str:
    formatted_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk["metadata"]
        source_info = f"Файл: {meta.get('source_file', '?')}, Стр. {meta.get('page_number', '?')}, Тип: {meta.get('doc_type', '?')}, Контрагент: {meta.get('counterparty', '?')}"
        formatted_parts.append(f"[ДОКУМЕНТ {i}]\n{source_info}\nТекст: {chunk['text']}\n")
    return "\n".join(formatted_parts)

SYSTEM_PROMPT = """Ты — строгий юридический ассистент ООО «ФЛАЙ-НСК».
Отвечай ТОЛЬКО на основе контекста. Если ответа нет, скажи: "В документах информация отсутствует".
ОБЯЗАТЕЛЬНО цитируй источник в формате: [Источник: Имя_Файла.pdf, стр. X].
Если есть противоречия между Договором и Протоколом разногласий, приоритет у Протокола."""

async def generate_answer(query: str, context_str: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\n\nКОНТЕКСТ:\n{context_str}\n\nВОПРОС: {query}\n\nОТВЕТ:"
    response = await ollama_client.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False, "options": {"temperature": 0.1, "num_predict": 600}}
    )
    response.raise_for_status()
    return response.json()["response"].strip()

# ==========================================
# 6. ЭНДПОИНТЫ (ROUTES)
# ==========================================
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Contract Analyzer RAG API is running", "docs": "/docs"}

@app.get("/health", tags=["System"])
async def health_check():
    """Deep Health Check: проверяет не только API, но и Ollama."""
    try:
        res = await ollama_client.get("http://localhost:11434/api/tags")
        ollama_status = "UP" if res.status_code == 200 else "DOWN"
    except Exception:
        ollama_status = "DOWN"
        
    return {
        "status": "UP" if ollama_status == "UP" else "DEGRADED",
        "faiss_vectors": faiss_index.ntotal if faiss_index else 0,
        "ollama": ollama_status
    }

@app.post("/api/v1/ask", response_model=QueryResponse, tags=["RAG"])
async def ask_question(request: QueryRequest):
    start_time = time.time()
    
    try:
        # 1. Embedding
        query_vector = np.array([await get_embedding(request.question)], dtype=np.float32)
        
        # 2. Retrieval
        chunks = retrieve_context(query_vector, request.top_k)
        
        # 3. Formatting
        context_str = format_context_for_llm(chunks)
        
        # 4. Generation
        answer = await generate_answer(request.question, context_str)
        
        # 5. Response
        sources = [
            SourceCitation(
                file=c["metadata"].get("source_file"),
                page=c["metadata"].get("page_number"),
                counterparty=c["metadata"].get("counterparty"),
                doc_type=c["metadata"].get("doc_type"),
                score=round(c["score"], 4)
            ) for c in chunks
        ]
        
        latency = round(time.time() - start_time, 2)
        print(f"✅ Запрос обработан за {latency} сек: '{request.question[:50]}...'")
        
        return QueryResponse(answer=answer, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Pipeline Error: {str(e)}")

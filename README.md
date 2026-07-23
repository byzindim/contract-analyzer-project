# <span style="display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:10px;font-size:18px;line-height:1;">⚖️</span> RAG-Анализатор Юридических Договоров (Contract Analyzer V2)

> Enterprise-Ready RAG-система для интеллектуального анализа юридических документов с 4-х ступенчатым гибридным поиском, кросс-языковой фильтрацией и строгой валидацией фактов.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen_2.5_14B-9cf)](https://ollama.com)
[![Embeddings](https://img.shields.io/badge/Embeddings-E5--Small-orange)](https://huggingface.co/intfloat/multilingual-e5-small)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com)
[![Metrics](https://img.shields.io/badge/Recall_Improvement-+310%25-brightgreen)]()

---

## <span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">📄</span> Что это

Production-ready RAG-система для автоматизации анализа корпоративных договоров, спецификаций и протоколов разногласий. Система использует полностью локальные LLM (гарантия конфиденциальности данных), специализированные эмбеддинги и продвинутые методы фильтрации шума.

**Бизнес-кейс:** замена ручного поиска условий по десяткам страниц документов → юрист получает точный, цитируемый ответ со ссылкой на конкретную статью и страницу за 2-3 минуты. Снижение рисков финансовых потерь из-за пропущенных штрафных санкций.

---

## <span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">✨</span> Ключевые особенности

- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Advanced Hybrid Search:** Семантический FAISS (`multilingual-e5-small`) + Лексический BM25 (`pymorphy3`) + слияние через Weighted RRF (веса 1.0 / 0.3).
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Query Rewriting:** Автоматическое расширение запроса юридическими синонимами через LLM перед поиском (например, "штраф" → "штраф, пеня, неустойка").
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Fuzzy Metadata Filtering:** Решение проблемы кросс-языкового сопоставления (кириллица в запросе vs латиница в метаданных) через транслитерацию (`unidecode`) и алгоритм Левенштейна (`thefuzz`).
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Cross-Encoder Reranking:** Финальная очистка Топ-20 → Топ-5 с помощью легкой модели `rubert-tiny2` для максимального удаления шума.
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Grounded Generation & Self-Correction:** Строгий JSON-вывод (`format="json"`) + алгоритмическая пост-проверка: все числа и проценты из ответа модели сверяются с исходным текстом контекста.
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Честная Оценка (Custom Evals):** Кастомный LLM-as-a-Judge с Chain of Thought и явной рубрикой, устраняющий проблему Prompt Anchoring (бинарного смещения оценок).

---

## <span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">🚀</span> Быстрый старт

### Вариант 1: Через Docker (Рекомендуется)

git clone https://github.com/byzindim/contract-analyzer-v2.git
cd contract-analyzer-v2

# Настройка окружения
cp .env.example .env

# Запуск всех сервисов (API + Ollama)
docker-compose up --build
# → API: http://localhost:8000/docs
# → Ollama: http://localhost:11434

### Вариант 2: Локальный запуск (без Docker)
#### 1. Установить Ollama и скачать модели
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:14b
# Модель эмбеддингов загружается через Python (sentence-transformers)

#### 2. Установить Python-зависимости
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

#### 3. Запустить FastAPI
uvicorn app.main:app --reload
# → http://localhost:8000/docs

<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">⚙️</span> Архитектура (Advanced RAG Pipeline)
```
                      Запрос пользователя
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Query Rewriting (LLM)│  Добавление юридических синонимов
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Fuzzy Metadata Filter │  unidecode + thefuzz (Кириллица ↔ Латиница)
                  └───────────┬───────────┘
                              │ Отсечение 90% шума
                              ▼
                  ┌───────────────────────┐
                  │   Hybrid Retrieval    │  FAISS (E5-small) + BM25 (pymorphy3)
                  │   + Weighted RRF      │  Слияние с весами: FAISS=1.0, BM25=0.3
                  └───────────┬───────────┘
                              │ Top-20 чанков
                              ▼
                  ┌───────────────────────┐
                  │ Cross-Encoder Rerank  │  rubert-tiny2 (глубокая семантическая оценка)
                  └───────────┬───────────┘
                              │ Top-5 Parent-Text чанков
                              ▼
                  ┌───────────────────────┐
                  │ Generator (Qwen 14B)  │  format="json", temperature=0.0
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Self-Correction      │  Алгоритмическая сверка чисел с контекстом
                  └───────────────────────┘
```

<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">📡</span> API
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI REST API (v1)                               │
│                    http://localhost:8000/docs (Swagger UI)                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  POST /api/v1/ask                                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Описание: Задать вопрос по базе юридических документов                     │
│                                                                             │
│  Request:                                                                   │
│  {                                                                          │
│    "question": "Какой размер пени за просрочку у ООО АэроТехКомплект?"      │
│  }                                                                          │
│                                                                             │
│  Response:                                                                  │
│  {                                                                          │
│    "request_id": "req_9a2b3c4d",                                            │
│    "answer": "0,1% от стоимости непоставленного Товара за каждый день...",  │
│    "sources": ["2024-05-12_CONTRACT...pdf, стр. 4"],                        │
│    "self_correction_triggered": false,                                      │
│    "latency_ms": 4250                                                       │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  GET /health                                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Описание: Проверка статуса API, Ollama и загрузки индексов                 │
│                                                                             │
│  Response:                                                                  │
│  {                                                                          │
│    "status": "healthy",                                                     │
│    "ollama_available": true,                                                │
│    "model": "qwen2.5:14b",                                                  │
│    "faiss_index_loaded": true,                                              │
│    "bm25_index_loaded": true                                                │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">📊</span> Метрики и Оценка (Evaluation)
Система протестирована на кастомном Ground Truth датасете из 10 сложных юридических вопросов (включая кейсы с конфликтующими условиями в Договорах и Протоколах разногласий).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVALUATION PIPELINE (Ground Truth)                        │
│              Тестовый датасет: 10 вопросов (Юридическая сфера)               │
│              Метод оценки: Custom LLM-as-a-Judge + Chain of Thought          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  МЕТРИКИ КАЧЕСТВА RAG-СИСТЕМЫ (До vs После модернизации)                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Context Recall: 0.19  ──────▶  0.67  (+310%)                       │   │
│  │  ████████████████████████████████████                              │   │
│  │  Резкий рост за счет Query Rewriting и E5-эмбеддингов              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Faithfulness: 0.47  ──────▶  0.67  (+68%)                          │   │
│  │  ████████████████████████████████████                              │   │
│  │  Снижение галлюцинаций за счет 14B модели и Self-Correction        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  JSON Validity: 100%                                                │   │
│  │  ████████████████████████████████████████████████████████████████  │   │
│  │  Ни одного падения парсинга (Constrained Decoding)                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  МЕТОДОЛОГИЯ ОЦЕНКИ                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  1. Custom LLM-as-a-Judge (Qwen 2.5 14B) с явной рубрикой (0.0-1.0)        │
│  2. Chain of Thought: Судья сначала пишет reasoning, потом выставляет балл │
│  3. Checkpointing: Сохранение результатов после каждого вопроса            │
└─────────────────────────────────────────────────────────────────────────────┘
```

<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">🛠️</span> Стек технологий:
1. LLM Инференс: Ollama (локально, qwen2.5:14b для генерации и rewriting).
2. Эмбеддинги: intfloat/multilingual-e5-small (с префиксами query:/passage: и Mean Pooling).
3. Vector DB: FAISS (IndexFlatIP для нормализованных векторов, Cosine Similarity).
4. Lexical Search: rank-bm25 + pymorphy3 (лемматизация).
5. Reranking: cointegrated/rubert-tiny2 (Cross-Encoder).
6. Backend: FastAPI, Pydantic V2, Uvicorn, httpx.
7. Утилиты: thefuzz + unidecode (Fuzzy Matching), PyMuPDF (парсинг).
8. Инфраструктура: Docker, docker-compose, Google Drive (Stateless-архитектура).


<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">📂</span> Структура проекта

```
contract-analyzer-v2/
├── app/
│   ├── api/           # FastAPI роуты и middleware
│   ├── core/          # Конфиги и lifespan (warm-up)
│   ├── llm/           # Ollama client с retry-логикой
│   ├── rag/           # Hybrid Search, RRF, Reranker, Self-Correction
│   └── schemas/       # Pydantic модели (DTO)
├── rag_artifacts/
│   ├── parent_child_chunks.json  # Structure-Aware чанки
│   ├── faiss_index_e5.index      # FAISS индекс (E5-small)
│   ├── bm25_v2.pkl               # BM25 индекс
│   └── knowledge_graph.json      # Lightweight GraphRAG (ORG ↔ MONEY)
├── scripts/
│   └── evaluate.py    # Скрипт оценки на датасете (Custom LLM-as-a-Judge)
└── docker-compose.yml
```

<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">🗺️</span> Roadmap (Зоны роста):
- Fine-tuning Эмбеддингов: Дообучение e5-small на размеченных юридических парах вопрос-ответ для дальнейшего роста Recall.
- Query Decomposition: Разбиение сложных multi-hop запросов (например, "найти все контракты ООО Х, где штрафы выше Y") на цепочку простых запросов.
- Апгрейд LLM: Переход на 32B/70B модели (при наличии соответствующего GPU) для еще более строгого следования сложным юридическим инструкциям.
- Advanced Metadata Filtering: Интеграция полноценного парсинга иерархии документов (Договор → Доп. соглашения → Протоколы разногласий) для автоматического разрешения конфликтов условий.

<p align="center">
Сделано с ❤️ и инженерным подходом |
<a href="https://github.com/byzindim">Дмитрий Бызин (AI Engineer)</a>
</p>

# ResearchMind  
**Your AI-powered Academic Research Assistant**  

ResearchMind is a full-stack web application that allows researchers, students, and professionals to **upload, search, and interact** with academic papers using **natural language queries**. Powered by **Django**, **LangChain**, and **ChromaDB**, the platform enables **semantic search** and **context-aware question answering** on uploaded research documents.  

## Features  
- **Research Paper Uploads** – Supports PDF uploads with AWS S3 storage.  
- **Semantic Search** – Uses **MiniLM** embeddings and **ChromaDB** for fast vector-based retrieval.  
- **Natural Language Q&A** – Ask questions about your papers and get context-aware answers using **LangChain** with OpenAI/Hugging Face models.  
- **RAG (Retrieval-Augmented Generation)** – Combines vector search with LLMs for precise, reference-backed responses.  
- **Paper Management Dashboard** – View and manage all uploaded research papers.  

---

## Tech Stack  

### **Backend**  
- **Django** & **Django REST Framework** – API development and backend logic  
- **LangChain** – LLM orchestration, prompt chaining, and RAG pipeline  
- **ChromaDB** – Vector database for semantic retrieval  
- **Hugging Face** – MiniLM for embedding generation  
- **OpenAI API** – LLM-powered answer generation  
- **AWS S3** – Cloud storage for uploaded PDFs  

### **Frontend**  
- **HTML/CSS/JS** or React-based UI (depending on version)  
- Integrated **REST API calls** to backend for uploads and queries  

### **Deployment**  
- **Backend** – Hosted on **Render** (Django + Gunicorn + SQLite for metadata)  
- **Storage** – AWS S3 for file persistence  
- **Environment Management** – `.env` variables for API keys and DB credentials  

---

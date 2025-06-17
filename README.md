# Hate Speech Detection System

The Hate Speech Detection System is an advanced, modular platform for detecting and analyzing hate speech in both text and audio content. It leverages state-of-the-art AI models, policy retrieval, and explainable reasoning to help moderators, researchers, and organizations ensure safe and compliant online environments.

---

## Features

- **Text Analysis:**  
  Instantly analyze any text for hate speech, toxicity, offensiveness, neutrality, or ambiguity.  
  Get confidence scores, detailed AI explanations, and references to relevant policies.

- **Audio Analysis:**  
  Record or upload audio, transcribe it in real time, and analyze the transcribed text for hate speech using the same robust pipeline as text analysis.

- **Policy Retrieval:**  
  Retrieve and display relevant legal and platform policies (e.g., US law, Reddit, Twitter, Meta, Google, IPC) that match the analyzed content, providing context and transparency.

- **AI Reasoning:**  
  Receive detailed, explainable AI reasoning for each classification, referencing specific policies and contextual factors for transparency and trust.

- **Action Recommendation:**  
  Get recommended moderation actions (e.g., remove, flag, allow) based on classification, confidence, and policy context.

- **History & Download:**  
  All analyses (text and audio) are stored in a searchable, downloadable history with source, timestamp, and classification, making it easy to audit or review past moderation decisions.

---

## Project Structure
bash
```
hatespeechproject/
| 
├── backend/ 
│   ├── agents/                 # Core AI and retrieval agents 
|   |   ├──action_agent.py
|   |   ├──error_handler.py
|   |   ├──hate_speech_agent.py
|   |   ├──reasoning_agent.py
│   |   └── retriever_agent.py
|   |
│   ├── api/                     # FastAPI endpoints and services 
|   |   ├──analysis_services.py
│   |   └── api_main.py
|   |
│   ├── schemas/                 # Pydantic schemas for API 
|   |   └── text_schema.py 
│   ├── utils/                   # Utility modules (logging, embeddings, etc.) 
|   |   ├──embedding_utils.py
|   |   ├──logging_utils.py
│   |   └── qdrant_store.py
|   |
│   └── config.py                # Contains configuration information
|   |      
│   └── main.py                  # FastAPI app entry point 
│ 
├── frontend/ 
│   ├── pages/ 
│   │   ├── text_analysis.py     # Streamlit page for text analysis 
│   │   ├── audio_analysis.py    # Streamlit page for audio analysis 
│   │   └── history.py           # Streamlit page for analysis history 
│   │ 
│   ├── api_client.py            # Handles API requests from frontend 
|   |
│   └── app.py                   # Streamlit app entry point 
│ 
├── data/ 
│   └── policy_data/             # Policy documents for retrieval 
│       ├── google_policy.txt 
│       ├── ipc_section.txt   
│       ├── meta_policy.txt
│       ├── reddit_policy.txt
│       ├── twitter_policy.txt 
│       └── us_hate_law_policy.py  
|
├── tests/                       # Unit tests for backend agents
│   ├── text_action_agent.py   
│   ├── test_error_handler.py     
│   ├── test_hate_speech_agent.py   
│   ├── test_reasoning_agent.py    
│   └── test_retriver_agent.py                     
│   
├── requirements.txt             # Python dependencies 
|
├── docker-compose.yml           # Docker Compose file
|
├── pyproject.toml               # Project metadata and dependencies
|
└── README.md                    # Project documentation

```

## Getting Started

### 1. **Setup the Virtual Environment or uv**

```bash
python -m venv venv     # for virtual environment
pip install uv          # for uv
```
### 2. **Activate the Virtual Environment or uv**

```bash
venv\Scripts\activate     # for virtual environment
 uv init .                # for uv
```

### 3. **Install Dependencies**

```bash
pip insall -r requirements.txt   # for virtual enviornment
uv add -r requirements.txt       # for uv
```

### 4. **Start the Backend API**

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. **Start the Frontend**

```bash
streamlit run .\frontend\app.py
```

### 6. **Access the App**

- Open your browser and go to: http://localhost:8501


## Configuration

- **API Base URL:**

    Set in the Streamlit sidebar under "API Settings" 
    ```bash 
    default: http://localhost:800<vscode_annotation_details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'>0</vscode_annotation>
    ```

- **Policy Data:**

    Add or update policy documents in ```data/policy_data/``` as needed.

- **Environment Variables:**

    Set your Azure/OpenAI API keys and endpoints in your environment or ```.env``` file as required by ```backend/config.py``` .

## Running Tests

```bash
pytest
```

## Technologies Used
- Streamlit (Frontend)
- FastAPI (Backend)
- OpenAI/Azure OpenAI (LLM)
- Qdrant (Vector DB for policy retrieval)
- SpeechRecognition (Audio transcription)
- Plotly (Charts)
- Pandas, NumPy, Pytest, etc.

## Notes
- Make sure your microphone is enabled for audio analysis.
- The backend must be running for the frontend to analyze content.
- All analysis history (text and audio) is available for download as CSV.
- The system is modular and can be extended with new policies, models, or moderation strategies.
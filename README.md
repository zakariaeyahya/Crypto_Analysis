# CryptoVibe: Sentiment Analysis for Crypto Markets 🚀

[![Build Status](https://github.com/kayou-s/Crypto_Analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/kayou-s/Crypto_Analysis/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React Version](https://img.shields.io/badge/react-18.2.0-blue.svg)](https://reactjs.org/)

CryptoVibe is a comprehensive platform for sentiment analysis of the cryptocurrency market. It leverages data from social media and financial sources, processes it through automated pipelines, and provides insights via an interactive dashboard and an intelligent RAG-powered chatbot.

## 📖 Table of Contents

- [✨ Key Features](#-key-features)
- [📸 Demo/Screenshots](#-demoscreenshots)
- [🛠️ Prerequisites](#️-prerequisites)
- [⚙️ Installation](#️-installation)
- [🚀 Usage](#-usage)
- [🔧 Configuration](#-configuration)
- [🏗️ Project Structure](#️-project-structure)
- [🧪 Testing](#-testing)
- [🤝 Contributing](#-contributing)
- [🛣️ Roadmap](#️-roadmap)
- [📄 License](#-license)
- [🙏 Credits](#-credits)
- [📞 Contact](#-contact)

## ✨ Key Features

*   ** Multi-Source Data Ingestion:** Collects data from Reddit (PRAW), Kaggle, and cryptocurrency prices from Yahoo Finance.
*   **🤖 Automated Data Pipelines:** Uses Apache Airflow for robust, automated data processing workflows.
*   **🧠 Advanced Sentiment Analysis:** Employs fine-tuned RoBERTa models and a custom VADER lexicon for nuanced sentiment analysis.
*   **📈 In-depth Market Analysis:** Provides insights into correlation, lag analysis, and entity extraction.
*   **🌐 Interactive Web Dashboard:** A React-based frontend for visualizing market sentiment, trends, and analysis.
*   **💬 RAG-Powered Chatbot:** An intelligent chatbot using Retrieval-Augmented Generation (RAG) with Groq and Pinecone to answer user queries.
*   **🐳 Containerized Architecture:** Utilizes Docker for consistent development and deployment environments.

## 📸 Demo/Screenshots

Here are some of the diagrams that illustrate the project's architecture and flow:

| Global Architecture | Data Flow | RAG Pipeline |
|---|---|---|
| <img src="./diagrams/Architecture_Globale_CryptoVibe.png" width="300"> | <img src="./diagrams/Flux_Donnees_Pipeline.png" width="300"> | <img src="./diagrams/Sequence_Chatbot_RAG.png" width="300"> |

*(More screenshots of the dashboard and application in action to be added.)*

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

*   **Python:** Version 3.10+
*   **Node.js:** Version 18+
*   **npm:** Version 9+
*   **Docker & Docker Compose:** For running the Airflow pipelines.
*   **Git:** For cloning the repository.

You will also need API keys for:

*   **Pinecone:** For the vector database.
*   **Groq:** For the LLM.
*   **Reddit:** (Optional) For scraping new data.

For detailed instructions, refer to the [Installation Documentation](./docs/INSTALLATION.md).

## ⚙️ Installation

Here is a summary of the installation process. For a complete guide, please see [INSTALLATION.md](./docs/INSTALLATION.md).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kayou-s/Crypto_Analysis.git
    cd Crypto_Analysis
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    python -m venv venv
    # Activate the virtual environment
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    pip install -r requirements.txt
    # Create and configure your .env file as per docs/INSTALLATION.md
    ```

3.  **Frontend Setup:**
    ```bash
    cd dashboard
    npm install
    ```

4.  **Indexer les documents (pour le RAG):**
    ```bash
    cd backend
    python scripts/index_documents.py --clear
    ```

## 🚀 Usage

To run the application, you'll need to start both the backend and frontend servers in separate terminals.

1.  **Start the Backend Server:**
    ```bash
    cd backend
    # Activate the virtual environment if you haven't already
    uvicorn app.main:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.

2.  **Start the Frontend Application:**
    ```bash
    cd dashboard
    npm start
    ```
    The dashboard will be accessible at `http://localhost:3000`.

## 🔧 Configuration

The project's main configuration is handled by environment variables.

*   **Backend:** Create a `.env` file in the `backend` directory. See `docs/INSTALLATION.md` for details on the required variables like `PINECONE_API_KEY` and `GROQ_API_KEY`.
*   **Airflow:** The Airflow services are configured via `.env.airflow` and `docker-compose.yml`.

For more details on configuration options, refer to the respective documentation files in the `docs` directory.

## 🏗️ Project Structure

The project is organized into several key directories:

```
├── airflow/         # Airflow DAGs and configuration
├── analysis/        # Scripts for data analysis
├── backend/         # FastAPI application and RAG module
├── dashboard/       # React frontend
├── data/            # Raw, processed, and analyzed data
├── data_cleaning/   # Scripts for data cleaning
├── docs/            # Project documentation
├── extraction/      # Data extraction scripts
├── Finetuning/      # NLP model finetuning scripts
└── ...
```

For a detailed breakdown, see the [Architecture Documentation](./docs/ARCHITECTURE.md).

## 🧪 Testing

The project includes tests for various components:

*   **Backend:**
    ```bash
    cd backend
    # Run all RAG tests
    bash tests/rag/run_all_tests.sh
    # Test the API
    bash test_api.sh
    ```
*   **Dashboard:**
    ```bash
    cd dashboard
    npm test
    ```
*   **Airflow DAGs:**
    ```bash
    # Inside the Airflow container or with a local Airflow setup
    pytest tests/test_dag_validation.py
    ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a pull request.

## 🛣️ Roadmap

*   [ ] Enhance the dashboard with more advanced visualizations.
*   [ ] Add support for more cryptocurrencies.
*   [ ] Integrate more data sources (e.g., Twitter, news articles).
*   [ ] Improve the RAG chatbot's capabilities with more advanced context handling.
*   [ ] Deploy the application to a cloud platform.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Credits

This project was made possible by the following key technologies and their communities:

*   [FastAPI](https://fastapi.tiangolo.com/)
*   [React](https://reactjs.org/)
*   [Apache Airflow](https://airflow.apache.org/)
*   [Pinecone](https://www.pinecone.io/)
*   [Groq](https://groq.com/)
*   [Hugging Face Transformers](https://huggingface.co/transformers/)



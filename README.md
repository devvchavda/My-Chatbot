# 🤖 Conversational AI with LangGraph & Streamlit

A powerful and intelligent chatbot built with **Streamlit**, **LangGraph**, and **Google Gemini**. This application features a responsive user interface, supports both text and voice input, and leverages powerful tools to provide dynamic responses, including file generation and data visualization.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://my-chatbot-almc.onrender.com/) ← **Try it here!**



***

## ✨ Features

* **🗣️ Voice & Text Input**: Interact with the chatbot via typing or speaking.
* **🧠Backend**: Powered by LangGraph to manage complex conversational flows and state.
* **🛠️ Tool Integration**: The agent can use custom tools to generate plots, create downloadable files, and perform other actions.
* **💬 Multi-Chat History**: Seamlessly create and switch between multiple conversations, with all history saved.
* **🚀 Real-time Streaming**: Responses are streamed token-by-token for a dynamic user experience.

***

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **Backend & Orchestration**: LangGraph
* **Language Model**: Google Gemini
* **Speech-to-Text**: `streamlit-audiorec` & `speech-recognition`

***

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

* Python 3.9+
* A virtual environment tool (`venv`)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    * Create a `.env` file in the root directory.
    * Add your API keys (e.g., for Google Gemini):
        ```
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
    Open your browser and navigate to `http://localhost:8501`.

***

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

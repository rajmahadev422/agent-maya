# Maya - AI Chat Assistant

A FastAPI-based chat application that leverages the Qwen3 model for conversational AI with tool integration capabilities.

## Key Features

- **Real-time Chat**: Stream responses with intermediate thinking steps and tool calls
- **Persistent Chat History**: Stores conversations in JSON files for future reference
- **Tool Integration**: Executes external tools via Ollama API (e.g., code execution, data retrieval)
- **User-Friendly Interface**: Web interface accessible at `http://127.0.0.1:4220`

## How to Use

1. Start the application:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 4220
   ```

2. Access the interface at: `http://127.0.0.1:4220`

3. Start a new chat or load existing conversations through the interface

## Technical Details

- **Model**: Qwen3 (4 billion parameter version)
- **Data Storage**: JSON chat history files stored in `PROJECT_DIR/maya`
- **Tool Execution**: Uses Ollama API for external tool interactions
- **Real-time Processing**: Streams responses with thinking steps and tool results

> **Note**: This application is designed to run locally with Python 3.10+ and requires the Ollama service to be running for tool execution.
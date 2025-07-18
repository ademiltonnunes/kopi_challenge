# Kopi Challenge - Debate Chatbot API

## Overview
This project implements an API for a chatbot that can hold a debate and attempt to convince the other side of its views, regardless of how irrational the point. The bot stands its ground and maintains a persuasive, cohesive conversation.

## Features
- Start a new debate conversation or continue an existing one
- Bot always stands its ground on the original topic
- Persuasive, context-aware responses
- Conversation history (last 5 messages per side)
- Fully containerized with Docker and Docker Compose
- Postgres database for persistence
- OpenAI API integration

## API Interface
### Request
```json
POST /chat
{
    "conversation_id": "text" | null,
    "message": "text"
}
```

### Response
```json
{
    "conversation_id": "text",
    "message": [
        { "role": "user", "message": "text" },
        { "role": "bot", "message": "text" }
    ]
}
```
- The `message` array contains the 5 most recent messages on both sides, with the most recent last.

## Endpoints
- `POST /chat` - Start or continue a debate
- `GET /conversations` - List all conversations
- `GET /conversations/{conversation_id}/messages` - List all messages in a conversation
- `GET /` - Root endpoint with docs link
- Interactive docs: `/docs`

## **Access the API**
   - [http://localhost:8000](http://localhost:8000)
   - Swagger-Docs: [http://localhost:8000/docs](http://localhost:8000/docs)


## Setup & Running (On Docker)

### Prerequisites
<details>
<summary><b>Docker and Docker Compose</b></summary>

#### macOS
1. Install Docker Desktop for Mac
   - Download from [Docker's official website](https://www.docker.com/products/docker-desktop)
   - Docker Desktop includes both Docker Engine and Docker Compose
   - Follow the installation wizard

#### Windows
1. Install Docker Desktop for Windows
   - Download from [Docker's official website](https://www.docker.com/products/docker-desktop)
   - Ensure WSL 2 is installed (Docker Desktop will prompt if not)
   - Docker Desktop includes both Docker Engine and Docker Compose
   - Follow the installation wizard

#### Linux (Ubuntu/Debian)
```bash
    # Update package index
    sudo apt-get update

    # Install prerequisites
    sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up the repository
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine and Docker Compose
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```
</details>

### Environment Variables
**Before you do anything else, create a `.env` file in the project root with the following variables:**

```
OPENAI_API_KEY=insert_your_open_AI_API_key_here
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_USERNAME=kopi_user
POSTGRES_PASSWORD=kopi_pass@
POSTGRES_DB_NAME=kopi_challenge_db
```

1. **Create .env file**
   - Copy `.env.example` to the folder root and rename the file to `.env`
   - Or create an .env file and copy the example above

2. **OpenAI API Key**
    - Create an account on OpenAI: [https://openai.com/](https://openai.com/)
    - Once logged in to OpenAI, create an API key at: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
    - Paste the API key in the .env file under the variable `OPENAI_API_KEY`

3. **Add credit to OpenAI**
    - It may be necessary to add some credit to the OpenAI Platform. Even though it is using the cheapest LLM model, it may charge a few cents to communicate.
    - Visit: [https://platform.openai.com/settings/organization/billing/overview](https://platform.openai.com/settings/organization/billing/overview)
    - Add some credit to your OpenAI Platform account

### Build and run application
1. **Install and verify prerequisite installation**
    ```
    make install
    ```
    - This will verify if Docker is installed and running
2. **Build and run application**
   ```
   make run
   ```
   - This will start both the API and Postgres database in Docker.
3. **Run tests**
   ```
   make test
   ```
4. **Stop services**
   ```
   make down
   ```
5. **Remove all containers and volumes**
   ```
   make clean
   ```

> **Note:** Database tables are created automatically on application startup. No manual initialization is required.

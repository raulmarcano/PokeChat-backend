# PokeChat Backend

PokeChat Backend is the server-side component that powers the Pokémon chatbot application. This backend is built using **Python FastAPI** and integrates with **OpenAI GPT-4 mini** and the [Pokémon API](https://pokeapi.co/) to provide AI-powered responses about Pokémon. It handles requests from the frontend, manages memory, performs Pokémon comparisons, and fetches data from the Pokémon API.

## Features

- **AI Integration**: Uses **OpenAI GPT-4o mini** to generate meaningful AI-driven responses about Pokémon.
- **Pokémon Data**: Fetches detailed information about Pokémon from the [Pokémon API](https://pokeapi.co/).
- **Memory Management**: Manages user interactions and stores context for more personalized responses.
- **Pokémon Comparison**: Allows users to compare multiple Pokémon, examining stats, abilities, and more.
- **FastAPI**: The backend is built with **FastAPI**, which allows for high-performance, asynchronous API requests.

## Tech Stack

This project is built using:

- **Python** with **FastAPI** for building the RESTful API.
- **OpenAI GPT-4o mini** for generating AI-driven responses to user queries.
- **Pokémon API** for fetching data about Pokémon (e.g., stats, abilities, evolutions).
- **Uvicorn** for running the FastAPI server in a production environment.

## Installation

To run the PokeChat Backend locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/raulmarcano/PokeChat-backend.git
   cd PokeChat-backend
   ```
   
2. Create .env and set the OPENAI_API_KEY:
   ```bash
   echo OPENAI_API_KEY='your:api:key' > .env
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will be running on http://127.0.0.1:8000.
   

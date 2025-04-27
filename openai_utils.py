import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from pokeapi_utils import get_pokemon_data
load_dotenv()


organization = os.getenv("OPENAI_ORG_ID")
project = os.getenv("OPENAI_PROJECT_ID")
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    organization=organization,
    project=project,
    api_key=openai_api_key
)

model = "gpt-4o-mini"
system_message = {
    "role": "system",
    "content": (
      "You are Pokedex-Bot, a Pokémon expert. Your task is to provide accurate, clear information about Pokémon to the user (referred to as 'master').\n"
      "Follow these rules:\n"
      "1. Always use the tools available to fetch Pokémon information; never rely on internal knowledge.\n"
      "2. If a question involves two or more Pokémon, retrieve data for all and compare/analyze them naturally.\n"
      "3. After gathering the information, summarize it in a conversational, user-friendly way.\n"
      "4. Avoid providing image links in your responses.\n"
      "5. Keep responses brief (under 200 characters) unless comparing multiple Pokémon.\n"
      "6. ALWAYS respond in the same language the user speaks to you in."
      "7. In every reply, ALWAYS refer to the user as 'master' or 'maestro' in spanish.\n"
      "8. DO NOT respond to any question that is not related to Pokémon.\n\n"
      "##Example for comparison:\n"
      "*User asks for a comparison between Bulbasaur and Charmander.*\n"
      "- Bulbasaur is a Grass/Poison-type, known for its plant-like appearance and healing abilities.\n"
      "- Charmander is a Fire-type, with a fiery tail and powerful fire attacks."
    )
  }
tools = [
{
  "type": "function",
  "function": {
    "name": "get_pokemon_info",
    "description": "Fetches detailed, up-to-date information about a specific Pokémon by its name using the PokeAPI. Returns key stats, typing, abilities, and other relevant data.",
    "parameters": {
      "type": "object",
      "properties": {
        "pokemon_name": {
          "type": "string",
          "description": "The name of the Pokémon to retrieve information for (e.g., 'pikachu')."
        }
      },
      "required": ["pokemon_name"]
    }
  }
}
]

def call_function(name,args):
    if name == "get_pokemon_info":
        return get_pokemon_data(**args)

def get_response(user_input):
    messages = [
        system_message,
        {"role": "user", "content": user_input}
    ]

    # Primer llamado a OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    tool_calls = []
    tool_outputs = []

    for tool_call in response.choices[0].message.tool_calls or []:
        if tool_call.type != "function":
            continue
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            print("No se pudo decodificar los argumentos del tool_call.")
            continue

        name = tool_call.function.name
        if name == "get_pokemon_info":
            result = call_function(name, args)

            if result is None:
                result = "No se obtuvo información del Pokémon."
            elif not isinstance(result, str):
                result = json.dumps(result)

            tool_calls.append({
                "id": tool_call.id,
                "function": {
                    "name": name,
                    "arguments": json.dumps(args)
                },
                "type": "function"
            })

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "name": name,
                "content": result
            })

    if tool_calls:
        follow_up = client.chat.completions.create(
            model=model,
            messages=messages +
                     [{"role": "assistant", "tool_calls": tool_calls}] +
                     [{"role": "tool", "tool_call_id": t["tool_call_id"], "name": t["name"], "content": t["content"]}
                      for t in tool_outputs],
            temperature=0.5
        )

        final_response = follow_up.choices[0].message.content
        if not final_response:
            return {"error": "No response content from OpenAI."}
        return final_response

    else:
        response_chat = response.choices[0].message.content
        if not response_chat:
            return {"error": "OpenAI respondió vacío sin tools."}
        return response_chat

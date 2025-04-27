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

instructions= (
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

tools = [
{
    "type": "function",
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
]

def call_function(name,args):
    if name == "get_pokemon_info":
        return get_pokemon_data(**args)

def get_response(user_input, resp_id):
    prompt = [
        {"role": "user", "content": user_input}
    ]

    if not resp_id:    
        #Primera llamada a OpenAI
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=instructions,
            input=prompt,
            temperature=0.5,
            tools=tools,
            tool_choice="auto",
            store=True
        )
    else:
        #Llamada con resp_id previo
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=instructions,
            input=prompt,
            temperature=0.5,
            tools=tools,
            tool_choice="auto",
            previous_response_id=resp_id,
            store=True
        )

    #Iterar sobre tool_call para llamar a cada función
    tool_calls = []
    for tool_call in response.output:
        if tool_call.type != "function_call":
            continue
        if not hasattr(tool_call, "arguments") or not tool_call.arguments:
            print(f"[WARN] tool_call sin 'arguments': {tool_call}")
            continue
        try:
            args = json.loads(tool_call.arguments)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error al decodificar arguments: {tool_call.arguments} — {e}")
            continue

        name = tool_call.name
        result = call_function(name, args)

        tool_calls.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": str(result)
        })

    if tool_calls:
        # Segunda llamada a OpenAI con las tools_calls
        follow_up = client.responses.create(
            model="gpt-4o-mini",
            input=tool_calls,
            instructions=instructions,
            tools=tools,
            previous_response_id=response.id,
            temperature=0.5,
            store=True
        )
        final_response = follow_up.output_text
        return final_response, follow_up.id
    else:
        response_chat = response.output_text
        return response_chat, response.id

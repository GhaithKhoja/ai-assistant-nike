import os
import json
import subprocess
import itertools
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI
from collections import defaultdict
from scraper.db.database import search_products, search_new_releases, search_products_with_discounts

# Load environment variables from .env file
load_dotenv()

# Load the OpenAI key
api_key = os.getenv("OPENAI_KEY")

class Assistant:
    """
    Nike Air Jordan AI Assistant. 
    """
    def __init__(self, voice=False):
        # OpenAI Client
        self.client = OpenAI(api_key=api_key)
        
        # Array that will hold the history of messages
        self.messages = []
        
        # Set the model that we will use
        self.model = 'gpt-3.5-turbo' # Switch this out for gpt-4o for better performance
        
        # Limit of how many responses from the DB we pass to the assistant
        # Feel free to increase or decrease to see the difference
        self.limit = 20
        
        # Set if we should stream back by voice or text
        self.voice = voice
        
        # Set the system prompt and append it to the message
        system_prompt = """
        You are an AI assistant specialized in Nike Air Jordan products. Your goal is to provide helpful and accurate information to users about Air Jordans. Here's how you should act:
        Your role is to assist users in navigating the world of Nike Air Jordan products with ease and confidence. Stay knowledgeable, responsive, and friendly in all interactions.
        """
        
        # Add a command to make answers concise if voice flag is set
        if self.voice:
            system_prompt += ' Please provide concise and brief responses suitable for audio playback.'

        # Add the system prompt to the messages
        self.messages.append({"role": "system", "content": system_prompt})
    
    
    def add_user_message(self, message):
        """
        Adds a user message to the message history of the assistant.

        Args:
        - message (str): The user message to be added.
        """
        self.messages.append({"role": "user", "content": message})
        
    def add_tool_result(self, id, function_name, result):
        """
        Adds a tool call result message to the message history of the assistant.

        Args:
        - result (array): The array of the result to be returned.
        """
        self.messages.append({
            "tool_call_id": id,
            "role": "tool",
            "name": function_name,
            "content": result,
        })
        
    def tool_list_to_tool_obj(self, tools):
        """
        Converts a list of tool call objects into a structured dictionary format.

        Args:
        - tools (list): A list of tool call objects, where each object contains attributes like id, function, and type.

        Returns:
        - dict: A dictionary containing a single key "tool_calls" with a list of structured tool call dictionaries.

        The structure of each tool call dictionary in the returned list is as follows:
        - id (str or None): The identifier of the tool call.
        - function (dict): A dictionary containing:
            - arguments (str): The concatenated arguments for the tool function.
            - name (str or None): The name of the tool function.
        - type (str or None): The type of the tool call.

        Example:
        >>> tools = [
        ...     ToolCall(index=0, id="1", function=ToolFunction(name="func1", arguments="arg1"), type="type1"),
        ...     ToolCall(index=1, id="2", function=ToolFunction(name="func2", arguments="arg2"), type="type2")
        ... ]
        >>> result = tool_list_to_tool_obj(tools)
        >>> print(result)
        {'tool_calls': [{'id': '1', 'function': {'arguments': 'arg1', 'name': 'func1'}, 'type': 'type1'}, {'id': '2', 'function': {'arguments': 'arg2', 'name': 'func2'}, 'type': 'type2'}]}
        """
        # Initialize a dictionary with default values
        tool_calls_dict = defaultdict(lambda: {"id": None, "function": {"arguments": "", "name": None}, "type": None})

        # Iterate over the tool calls
        for tool_call in tools:
            # If the id is not None, set it
            if tool_call.id is not None:
                tool_calls_dict[tool_call.index]["id"] = tool_call.id

            # If the function name is not None, set it
            if tool_call.function.name is not None:
                tool_calls_dict[tool_call.index]["function"]["name"] = tool_call.function.name

            # Append the arguments
            tool_calls_dict[tool_call.index]["function"]["arguments"] += tool_call.function.arguments

            # If the type is not None, set it
            if tool_call.type is not None:
                tool_calls_dict[tool_call.index]["type"] = tool_call.type

        # Convert the dictionary to a list
        tool_calls_list = list(tool_calls_dict.values())

        # Return the result
        return {"tool_calls": tool_calls_list}
    
    def get_tools(self, first_call=False):
        """
        Returns the functions that the AI can use to answer questions
        
        if first_call is true, we will give the ability to the AI to not call a function
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for Nike Air Jordan products in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the product to search for"
                            },
                            "max_price": {
                                "type": "number",
                                "description": "Maximum price of the product"
                            },
                            "colors": {
                                "type": "string",
                                "description": "Colors of the product to search for"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the product to search for"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["low", "mid", "high", "basketball", "slides"],
                                "description": "Category of the product (low, mid, high, basketball, slides)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_products_with_discounts",
                    "description": "Search for Nike Air Jordan products with discounts in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the product to search for"
                            },
                            "max_price": {
                                "type": "number",
                                "description": "Maximum price of the product"
                            },
                            "colors": {
                                "type": "string",
                                "description": "Colors of the product to search for"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the product to search for"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["low", "mid", "high", "basketball", "slides"],
                                "description": "Category of the product (low, mid, high, basketball, slides)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_new_releases",
                    "description": "Search for new Nike Air Jordan releases in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the product to search for"
                            },
                            "max_price": {
                                "type": "number",
                                "description": "Maximum price of the product"
                            },
                            "colors": {
                                "type": "string",
                                "description": "Colors of the product to search for"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the product to search for"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["low", "mid", "high", "basketball", "slides"],
                                "description": "Category of the product (low, mid, high, basketball, slides)"
                            }
                        },
                        "required": []
                    }
                }
            }
        ]

        # If it's the first call, append a placeholder function
        if first_call:
            tools.append({
                "type": "function",
                "function": {
                    "name": "no_function_call",
                    "description": "This is a placeholder function. If no specific function is needed to answer the prompt, use this.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            })

        return tools

        
    def stream_response(self, message):
        """
        Streams a response back to the user.
        Can call functions from the tools to get data to answer a question.

        Args:
        - message (str): The user message to be added.
        """
        # Add user message
        self.add_user_message(message)
        
        # Iterate over the messages as they are streamed
        print("\n")
        print("Air Jordans AI Assistant: ")
        print("building response...", end='', flush=True)
        
        # Get the initital response
        response = self.client.chat.completions.create(
            model=self.model, 
            messages=self.messages,
            tools=self.get_tools(first_call=True), # Pass the tools the AI can use
            tool_choice="required", # Force a function call for the first use
            temperature=1 # Give it a bit of creativity and make it less deterministic
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        # Check what function the AI wants to call
        if tool_calls:
            # Append the assitant's request for a function call
            self.messages.append(response.choices[0].message)
            
            # Send the info for each function call and function response to the model
            for tool_call in tool_calls:
                # Parse function name and args
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Parse name if it exists
                name = function_args.get('name')
                
                # Parse description if it exists
                description = function_args.get('description')
                
                # Parse max_price if it exists
                max_price = function_args.get('max_price')
                
                # Parse colors if it exists
                colors = function_args.get('colors')
                
                # Parse category if it exists
                category = function_args.get('category')
                
                # define returned results
                results = []
                
                # Call the correct function
                if function_name == 'search_products':
                    results = search_products(
                        name=name,
                        max_price=max_price,
                        colors=colors,
                        description=description,
                        category=category,
                        limit=self.limit
                    )
                elif function_name == "search_products_with_discounts":   
                    results = search_products_with_discounts(
                        name=name,
                        max_price=max_price,
                        colors=colors,
                        description=description,
                        category=category,
                        limit=self.limit
                    )
                elif function_name == "search_new_releases": 
                    results = search_new_releases(
                        name=name,
                        max_price=max_price,
                        colors=colors,
                        description=description,
                        category=category,
                        limit=self.limit
                    )
                    
                # Append the result to the messages history
                self.add_tool_result(id=tool_call.id, function_name=function_name, result=results) 
                
        # Notify the user that the AI finishing building up the response
        sys.stdout.write('\r')  # Move the cursor back to the start of the line
        sys.stdout.write(' ' * len("Building response..."))  # Overwrite the previous message with spaces
        sys.stdout.write('\r')  # Move the cursor back to the start of the line again         
        
        if not self.voice:
            # Start the streaming completion
            stream = self.client.chat.completions.create(
                model=self.model, 
                stream=True,  # Set stream to True to receive messages in chunks
                messages=self.messages,
            )
            # Print the response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")  # Output final result
        else:
            # Get the response
            text_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )
            
            # Extract content from response
            content = text_response.choices[0].message.content

            # Define maximum length for each section (4096 characters)
            max_length = 4096

            # Split content into sections without cutting words
            sections = []
            current_section = ""
            for word in content.split():
                if len(current_section) + len(word) + 1 <= max_length:
                    if current_section:
                        current_section += " "
                    current_section += word
                else:
                    sections.append(current_section)
                    current_section = word
            
            # Append last section if any
            if current_section:
                sections.append(current_section)
                
            # Define the states for the dots - This is used for the Generating response text
            message = "Generating audio response..."
            # Print the message with moving dots
            sys.stdout.write(f"\r{message}")
            sys.stdout.flush()

            # Iterate over sections
            for section in sections:
                # Generate speech for the current section
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice="nova",  # Adjust voice as needed
                    input=section,
                )
                
                # Replace the message with the audio response that will be played
                sys.stdout.write("\r" + " " * (len(message) + 3) + "\r")  # Clear the line
                sys.stdout.write(f"{section}\n")
                sys.stdout.flush()
            
                # Save the response to a local file
                output_file = "voice_response.mp3"
                response.stream_to_file(output_file)

                # Play the saved MP3 file using macOS afplay command
                try:
                    subprocess.run(["afplay", output_file])
                except FileNotFoundError:
                    print("Error: 'afplay' command not found. Make sure you are using macOS.")
                except Exception as e:
                    print(f"Error occurred during playing: {e}")
                
    


from assistant.assistant import Assistant

def main():
    # Init the assistant
    assistant = Assistant()
    
    # Print welcome message
    print("\n")
    print("Welcome to the Nike Air Jordan Product Assistant!")
    print("I'm here to help you with all your inquiries about Nike Air Jordan products.")
    print("You can ask me questions like:")
    print("- \"What are the newest Air Jordan releases?\"")
    print("- \"Show me Air Jordan shoes with discounts.\"")
    print("- \"Tell me more about the Air Jordan 1 Retro High OG.\"")
    print("Feel free to ask anything related to Nike Air Jordan products.")
    print("Let's dive into the world of Air Jordans together!")
    print("\n")
    
    # Take user input
    while True:
        user_input = input("user: ")
        assistant.stream_response(user_input )  # Stream AI response
        
        # Allow user to input another question after the assistant's response
        print("\n")  # Print newline for readability

if __name__ == '__main__':
    main()

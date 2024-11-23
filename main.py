import asyncio
from ai_agent import AnchoringAgent
from ui import AnchoringUI

async def main():
    # Initialize the agent and UI
    agent = AnchoringAgent()
    ui = AnchoringUI()
    
    # Setup the initial UI
    ui.setup_layout()
    ui.display()
    
    while True:
        try:
            # Get user input
            user_input = ui.get_user_input()
            
            if user_input.lower() in ['exit', 'quit']:
                break
                
            if user_input.lower() == 'clear':
                agent.clear_history()
                ui.clear()
                ui.setup_layout()
                ui.display()
                continue
            
            # Show loading animation while getting response
            with ui.show_loading():
                response = await agent.get_response(user_input)
            
            # Update the UI with the new conversation and response
            ui.update_conversation(agent.conversation_history)
            ui.update_output(response)
            ui.display()
            
        except Exception as e:
            ui.update_output({"error": f"An error occurred: {str(e)}"})
            ui.display()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")

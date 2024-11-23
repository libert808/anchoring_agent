from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from rich import box
from rich.live import Live
from config import THEME
import os

class AnchoringUI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        # Get terminal size
        terminal_width = os.get_terminal_size().columns
        terminal_height = os.get_terminal_size().lines
        self.width = min(terminal_width, 120)  # Cap at 120 chars
        self.height = terminal_height
        
    def setup_layout(self):
        self.console.clear()
        # Create main layout
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Split main area into conversation and output
        self.layout["main"].split_row(
            Layout(name="conversation", ratio=2, minimum_size=30),
            Layout(name="output", ratio=3, minimum_size=40)
        )
        
        self._draw_header()
        self._draw_conversation_panel()
        self._draw_output_panel()
        self._draw_footer()
        
    def _draw_header(self):
        title = Text("AI Anchoring Assistant", justify="center")
        title.stylize(f"bold {THEME['primary']}")
        
        self.layout["header"].update(
            Panel(
                title,
                style=THEME['background'],
                border_style=THEME['accent'],
                box=box.ROUNDED,
                padding=(0, 2)
            )
        )
        
    def _draw_footer(self):
        help_text = Text("Type 'exit' to quit | 'clear' to reset", justify="center")
        help_text.stylize(THEME['text'])
        
        self.layout["footer"].update(
            Panel(
                help_text,
                style=THEME['background'],
                border_style=THEME['accent'],
                box=box.ROUNDED,
                padding=(0, 2)
            )
        )
        
    def _draw_conversation_panel(self):
        self.layout["conversation"].update(
            Panel(
                "",
                title="Conversation",
                title_align="left",
                style=THEME['background'],
                border_style=THEME['secondary'],
                box=box.ROUNDED,
                padding=(1, 2)
            )
        )
        
    def _draw_output_panel(self):
        self.layout["output"].update(
            Panel(
                "",
                title="Generated Anchoring",
                title_align="left",
                style=THEME['background'],
                border_style=THEME['primary'],
                box=box.ROUNDED,
                padding=(1, 2)
            )
        )
        
    def update_conversation(self, messages):
        conversation_text = Text()
        for msg in messages:
            if msg["role"] == "user":
                conversation_text.append("\n🧑 You: ", style=f"bold {THEME['text']}")
                conversation_text.append(f"{msg['content']}\n", style=THEME['accent'])
            elif msg["role"] == "assistant" and msg["role"] != "system":
                conversation_text.append("\n🤖 Assistant: ", style=f"bold {THEME['text']}")
                conversation_text.append(f"{msg['content']}\n", style=THEME['secondary'])
                
        self.layout["conversation"].update(
            Panel(
                conversation_text,
                title="Conversation",
                title_align="left",
                style=THEME['background'],
                border_style=THEME['secondary'],
                box=box.ROUNDED,
                padding=(1, 2)
            )
        )
        
    def update_output(self, content):
        if isinstance(content, dict):
            output_text = Text()
            
            if 'error' in content:
                output_text.append(f"Error: {content['error']}\n", style=f"bold {THEME['error']}")
                if 'raw_content' in content:
                    output_text.append(f"\nRaw Content:\n{content['raw_content']}", style=THEME['text'])
            else:
                # Display metadata
                if 'metadata' in content:
                    output_text.append("\n[METADATA]\n", style=f"bold {THEME['accent']}")
                    metadata = content['metadata']
                    output_text.append(f"Title: {metadata['title']}\n", style=THEME['text'])
                    output_text.append(f"Audience: {metadata['audience']}\n", style=THEME['text'])
                    output_text.append(f"Duration: {metadata['duration']}\n", style=THEME['text'])
                    output_text.append(f"Type: {metadata['type']}\n", style=THEME['text'])
                
                # Display content
                if 'content' in content:
                    output_text.append("\n[CONTENT]\n", style=f"bold {THEME['accent']}")
                    content_data = content['content']
                    
                    output_text.append("\nOpening:\n", style=f"bold {THEME['secondary']}")
                    output_text.append(f"{content_data['opening']}\n", style=THEME['text'])
                    
                    if content_data['points']:
                        output_text.append("\nMain Points:\n", style=f"bold {THEME['secondary']}")
                        for i, point in enumerate(content_data['points'], 1):
                            output_text.append(f"{i}. {point}\n", style=THEME['text'])
                            if i-1 < len(content_data['transitions']):
                                output_text.append(f"\nTransition:\n{content_data['transitions'][i-1]}\n", style=THEME['text'])
                    
                    output_text.append("\nClosing:\n", style=f"bold {THEME['secondary']}")
                    output_text.append(f"{content_data['closing']}\n", style=THEME['text'])
                
                # Display notes
                if 'notes' in content:
                    output_text.append("\n[NOTES]\n", style=f"bold {THEME['accent']}")
                    notes = content['notes']
                    output_text.append("\nDelivery Instructions:\n", style=f"bold {THEME['secondary']}")
                    output_text.append(f"{notes['delivery']}\n", style=THEME['text'])
                    output_text.append("\nTiming:\n", style=f"bold {THEME['secondary']}")
                    output_text.append(f"{notes['timing']}\n", style=THEME['text'])
                    output_text.append("\nKey Points to Emphasize:\n", style=f"bold {THEME['secondary']}")
                    output_text.append(f"{notes['emphasis']}\n", style=THEME['text'])
                
                if 'content' in content and isinstance(content['content'], str):
                    output_text.append(f"\n{content['content']}", style=THEME['text'])
        else:
            output_text = Text(str(content), style=THEME['text'])
            
        self.layout["output"].update(
            Panel(
                output_text,
                title="Generated Anchoring",
                title_align="left",
                style=THEME['background'],
                border_style=THEME['primary'],
                box=box.ROUNDED,
                padding=(1, 2)
            )
        )
        
    def get_user_input(self):
        self.console.print()
        prompt_text = Text("Enter your request: ", style=THEME['primary'])
        self.console.print(prompt_text, end="")
        return input()
        
    def display(self):
        self.console.print(self.layout)
        
    def show_loading(self):
        return self.console.status("[bold green]Generating response...", spinner="dots")
    
    def update_streaming_output(self, chunk):
        """Update the output panel with streaming content"""
        output_text = Text(chunk, style=THEME['text'])
        self.layout["output"].update(
            Panel(
                output_text,
                title="Generated Anchoring (Streaming)",
                title_align="left",
                style=THEME['background'],
                border_style=THEME['primary'],
                box=box.ROUNDED,
                padding=(1, 2)
            )
        )
        self.display()
            
    def clear(self):
        self.console.clear()

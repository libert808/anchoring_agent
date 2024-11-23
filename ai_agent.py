import openai
from config import OPENAI_API_KEY, OPENAI_BASE_URL, SYSTEM_PROMPT, MODEL_CONFIG
import xml.etree.ElementTree as ET
import asyncio

class AnchoringAgent:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        if OPENAI_BASE_URL:
            openai.base_url = OPENAI_BASE_URL
        
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def _parse_xml_response(self, xml_string):
        try:
            # Add root element if not present
            if not xml_string.startswith('<speech>'):
                xml_string = f'<speech>{xml_string}</speech>'
            
            root = ET.fromstring(xml_string)
            
            # Parse metadata
            meta = root.find('meta')
            metadata = {
                'title': meta.find('title').text if meta is not None and meta.find('title') is not None else '',
                'audience': meta.find('audience').text if meta is not None and meta.find('audience') is not None else '',
                'duration': meta.find('duration').text if meta is not None and meta.find('duration') is not None else '',
                'type': meta.find('type').text if meta is not None and meta.find('type') is not None else ''
            }
            
            # Parse content
            content = root.find('content')
            content_data = {
                'opening': content.find('opening').text if content is not None and content.find('opening') is not None else '',
                'points': [],
                'transitions': [],
                'closing': content.find('closing').text if content is not None and content.find('closing') is not None else ''
            }
            
            # Get all points and transitions
            if content is not None:
                main = content.find('main')
                if main is not None:
                    for child in main:
                        if child.tag == 'point':
                            content_data['points'].append(child.text if child.text else '')
                        elif child.tag == 'transition':
                            content_data['transitions'].append(child.text if child.text else '')
            
            # Parse notes
            notes = root.find('notes')
            notes_data = {
                'delivery': notes.find('delivery').text if notes is not None and notes.find('delivery') is not None else '',
                'timing': notes.find('timing').text if notes is not None and notes.find('timing') is not None else '',
                'emphasis': notes.find('emphasis').text if notes is not None and notes.find('emphasis') is not None else ''
            }
            
            return {
                'metadata': metadata,
                'content': content_data,
                'notes': notes_data
            }
            
        except Exception as e:
            return {
                'error': f'Failed to parse response: {str(e)}',
                'raw_content': xml_string
            }

    async def get_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        
        try:
            client = openai.AsyncClient(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL if OPENAI_BASE_URL else None)
            
            # Create a streaming completion
            stream = await client.chat.completions.create(
                messages=self.conversation_history,
                stream=True,
                **MODEL_CONFIG
            )
            
            collected_messages = []
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    collected_messages.append(chunk.choices[0].delta.content)
                    # You can yield partial messages here if needed
                    
            full_response = ''.join(collected_messages)
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
            # Try to parse as XML if it contains XML tags
            if '<' in full_response and '>' in full_response:
                return self._parse_xml_response(full_response)
            
            return {"content": full_response}
            
        except Exception as e:
            return {"error": f"Error getting response: {str(e)}"}

    def clear_history(self):
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

import openai
import base64
import json
import logging
from typing import Dict, Any
from config import Config

class GPTVisionAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.API_KEY)
        self.model = Config.VISION_MODEL
        self.max_tokens = 500
        self.timeout = 30

    def analyze(self, image_bytes: bytes, custom_prompt: str) -> Dict[str, Any]:
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            messages = [
                {
                    "role": "system",
                    "content": """Lütfen YANITINIZI JSON FORMATINDA verin. Örnek:
```json
{
  "action": "click|type|press|wait|draw|drag|scroll|complete",
  "params": {
    "x": 100,
    "y": 200,
    "duration": 0.5,
    "button": "left"
  },
  "reason": "Açıklama",
  "is_complete": false
}
```"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{custom_prompt}\n\nLÜTFEN YANITI YUKARIDAKİ JSON FORMATINDA VERİN!"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": Config.IMAGE_DETAIL
                            }
                        }
                    ]
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            raw_content = response.choices[0].message.content
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                # Eğer JSON içinde json varsa temizle
                cleaned = raw_content[raw_content.find('{'):raw_content.rfind('}')+1]
                return json.loads(cleaned)
            
        except Exception as e:
            logging.error(f"Analiz hatası: {str(e)}")
            return {
                "action": "wait",
                "params": {"duration": 1.0},
                "reason": str(e),
                "is_complete": False
            }
import os
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, GoogleAPICallError, InvalidArgument
from dotenv import load_dotenv

load_dotenv()

class AIDriver:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ .env 파일에 GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_key)

        self.model_pool = [
            "gemini-2.5-pro", 
            "gemini-3.0-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash"
        ]

        self.generation_config = {
            "temperature": 0.85,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

    def generate(self, prompt):
        for model_name in self.model_pool:
            try:
                model = genai.GenerativeModel(model_name=model_name, generation_config=self.generation_config)
                response = model.generate_content(prompt)
                if response.text:
                    return response.text
            except (ResourceExhausted, ServiceUnavailable, GoogleAPICallError):
                time.sleep(1)
                continue 
            except (InvalidArgument, Exception):
                continue
        return ""

    def generate_json(self, prompt):
        full_prompt = prompt + "\n\n응답은 반드시 JSON 형식으로만 작성해줘. 마크다운 코드 블록(```json) 없이 순수 텍스트로 줘."
        text = self.generate(full_prompt)
        if text:
            return text.replace('```json', '').replace('```', '').strip()
        return "{}"
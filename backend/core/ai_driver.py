import os
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, GoogleAPICallError, InvalidArgument
from dotenv import load_dotenv

# .env 로드 (API 키 가져오기)
load_dotenv()

class AIDriver:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ .env 파일에 GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_key)

        # ---------------------------------------------------------
        # [모델 이어달리기] 확실히 작동하는 모델 리스트
        # ---------------------------------------------------------
        self.model_pool = [
            "gemini-2.5-pro", 
            "gemini-3.0-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash"
        ]

        # 생성 설정
        self.generation_config = {
            "temperature": 0.85,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

    def generate(self, prompt):
        """
        모델 풀을 순회하며 성공할 때까지 시도하는 이어달리기 로직
        """
        for model_name in self.model_pool:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=self.generation_config
                )

                response = model.generate_content(prompt)
                
                if response.text:
                    return response.text
            
            except ResourceExhausted:
                time.sleep(1)
                continue 

            except (ServiceUnavailable, GoogleAPICallError):
                time.sleep(1)
                continue

            except (InvalidArgument, Exception):
                continue

        return ""

    def generate_json(self, prompt):
        """JSON 포맷 강제"""
        full_prompt = prompt + "\n\n응답은 반드시 JSON 형식으로만 작성해줘. 마크다운 코드 블록(```json) 없이 순수 텍스트로 줘."
        text = self.generate(full_prompt)
        if text:
            return text.replace('```json', '').replace('```', '').strip()
        return "{}"
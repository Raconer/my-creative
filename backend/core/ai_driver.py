import os
import time
import re  # 👈 정규표현식 추가
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, GoogleAPICallError, InvalidArgument
from dotenv import load_dotenv

# .env 로드
load_dotenv()

class AIDriver:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ .env 파일에 GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_key)

        # 모델 풀 (최신 모델명 확인 필요: 현재 Gemini 2.0/1.5 등이 주류)
        self.model_pool = [
            "gemini-2.0-flash", 
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]

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
                
                # 가끔 safety_ratings에 의해 차단될 경우 response.text가 에러를 냄
                if response and response.text:
                    return response.text
            
            except ResourceExhausted:
                # 할당량 초과 시 약간 대기 후 다음 모델로
                time.sleep(2)
                continue 

            except (ServiceUnavailable, GoogleAPICallError) as e:
                print(f"🌐 API 호출 오류 ({model_name}): {e}")
                time.sleep(1)
                continue

            except Exception as e:
                print(f"❌ 알 수 없는 오류 ({model_name}): {e}")
                continue

        return ""

    def extract_json(self, text: str) -> str:
        """
        텍스트 내부에 포함된 JSON만 추출하는 강력한 정규표현식 로직
        """
        if not text:
            return "{}"
        
        # 가장 바깥쪽의 { ... } 구조를 찾습니다 (마크다운 블록이 있어도 무관)
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            # 제어 문자 제거 (줄바꿈 등으로 인한 파싱 에러 방지)
            clean_json = re.sub(r'[\x00-\x1F\x7F]', '', clean_json)
            return clean_json
            
        return "{}"

    def generate_json(self, prompt):
        """JSON 포맷 추출 로직 강화"""
        full_prompt = (
            f"{prompt}\n\n"
            "--- IMPORTANT ---\n"
            "응답은 반드시 유효한 JSON 형식이어야 합니다. "
            "추가 설명이나 인사말 없이 오직 JSON 데이터만 출력하세요."
        )
        
        raw_text = self.generate(full_prompt)
        
        # 1. 정규표현식으로 { } 구간만 추출
        json_text = self.extract_json(raw_text)
        
        # 2. 마크다운 기호가 남아있을 경우를 대비한 2차 정지
        json_text = json_text.replace('```json', '').replace('```', '').strip()
        
        return json_text
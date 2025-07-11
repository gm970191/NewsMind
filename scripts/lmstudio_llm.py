#!/usr/bin/env python3
"""
LMStudioLLM: 纯本地LM Studio大模型API调用类，无业务逻辑
"""
import requests
from typing import Optional, List, Dict, Any

class LMStudioLLM:
    def __init__(self, api_url: str = "http://localhost:1234/v1/chat/completions", model: str = "qwen2-0.5b-instruct", timeout: int = 30):
        self.api_url = api_url
        self.model = model
        self.timeout = timeout

    def set_model(self, model: str):
        self.model = model

    def get_models(self) -> Optional[List[str]]:
        """获取本地服务支持的模型列表"""
        try:
            url = self.api_url.replace("/v1/chat/completions", "/v1/models")
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception:
            return None

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.1) -> Optional[str]:
        """标准OpenAI格式对话"""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            resp = requests.post(self.api_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            result = resp.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            return None
        except Exception:
            return None

    def simple_chat(self, prompt: str, system_prompt: str = "你是AI助手。", max_tokens: int = 1000) -> Optional[str]:
        """简化对话接口，自动拼装messages"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        return self.chat(messages, max_tokens=max_tokens)

    def is_available(self) -> bool:
        """测试API可用性"""
        try:
            test_msg = [
                {"role": "system", "content": "你是AI助手。"},
                {"role": "user", "content": "你好"}
            ]
            result = self.chat(test_msg, max_tokens=10)
            return result is not None
        except Exception:
            return False 
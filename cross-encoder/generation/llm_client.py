"""
llm_client.py — LLM Integration cho Legal RAG

Hỗ trợ 2 chế độ:
1. Dev mode: Model nhỏ (7B Q4), context 2-4K, iterate nhanh
2. Demo mode: Model tốt hơn, streaming, UX mượt

Backends:
- llama.cpp (local)
- OpenRouter API
- OpenAI-compatible API
- HuggingFace Transformers
"""

import os
import json
import time
import subprocess
import threading
from typing import Optional, List, Dict, Generator, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import urllib.request
import urllib.error


class LLMBackend(Enum):
    """Các backend LLM được hỗ trợ."""
    LLAMA_CPP = "llama_cpp"             # Local llama.cpp
    OPENROUTER = "openrouter"           # OpenRouter API
    OPENAI = "openai"                   # OpenAI API
    GEMINI = "gemini"                   # Google Gemini
    HUGGINGFACE = "huggingface"         # HuggingFace Transformers
    PLACEHOLDER = "placeholder"         # Placeholder for testing


class LLMMode(Enum):
    """Chế độ hoạt động."""
    DEV = "dev"         # Development: nhỏ, nhanh
    DEMO = "demo"       # Demo: tốt hơn, streaming


@dataclass
class LLMConfig:
    """Cấu hình LLM."""
    
    # Backend selection
    backend: LLMBackend = LLMBackend.PLACEHOLDER
    mode: LLMMode = LLMMode.DEV
    
    # Model paths/names
    model_path: Optional[str] = None    # Path cho local models
    model_name: str = "default"         # Model name cho API
    
    # Generation parameters
    max_tokens: int = 512
    temperature: float = 0.1            # Low for legal accuracy
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    
    # Context
    context_length: int = 4096          # Dev: 2-4K, Demo: 8K+
    
    # API settings
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    
    # Timeout
    timeout_seconds: int = 60
    
    # llama.cpp specific
    n_gpu_layers: int = -1              # -1 = all layers on GPU
    n_threads: int = 4
    
    # Streaming
    enable_streaming: bool = False


@dataclass
class LLMResponse:
    """Response từ LLM."""
    
    text: str
    finish_reason: str = "stop"
    tokens_used: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None
    raw_response: Optional[Dict] = None


class LLMClient:
    """
    Unified LLM Client cho Legal RAG.
    
    Auto-detect backend từ environment hoặc config.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._auto_detect_config()
        self._llama_process = None
        self._initialize_backend()
    
    def _auto_detect_config(self) -> LLMConfig:
        """Auto-detect config từ environment."""
        
        config = LLMConfig()
        
        # Check API keys
        if os.environ.get("OPENROUTER_API_KEY"):
            config.backend = LLMBackend.OPENROUTER
            config.api_key = os.environ["OPENROUTER_API_KEY"]
            config.model_name = "mistralai/mistral-7b-instruct"
        elif os.environ.get("OPENAI_API_KEY"):
            config.backend = LLMBackend.OPENAI
            config.api_key = os.environ["OPENAI_API_KEY"]
            config.model_name = "gpt-3.5-turbo"
        elif os.environ.get("GEMINI_API_KEY"):
            config.backend = LLMBackend.GEMINI
            config.api_key = os.environ["GEMINI_API_KEY"]
            config.model_name = "gemini-pro"
        else:
            # Check for local llama.cpp model
            model_paths = [
                Path("llama.cpp/models"),
                Path("models"),
                Path.home() / ".cache/llama.cpp/models"
            ]
            for mp in model_paths:
                if mp.exists():
                    gguf_files = list(mp.glob("*.gguf"))
                    if gguf_files:
                        config.backend = LLMBackend.LLAMA_CPP
                        config.model_path = str(gguf_files[0])
                        break
            
            if config.backend == LLMBackend.PLACEHOLDER:
                print("[LLMClient] No API key or local model found. Using placeholder mode.")
        
        return config
    
    def _initialize_backend(self):
        """Initialize các backends cần setup."""
        
        if self.config.backend == LLMBackend.LLAMA_CPP:
            self._check_llama_cpp()
        elif self.config.backend == LLMBackend.HUGGINGFACE:
            self._init_huggingface()
    
    def _check_llama_cpp(self):
        """Check llama.cpp installation."""
        # Check if llama-cli or main exists
        llama_paths = [
            "llama.cpp/build/bin/Release/main.exe",
            "llama.cpp/build/bin/main",
            "llama.cpp/main",
            "llama-cli",
        ]
        
        self._llama_executable = None
        for path in llama_paths:
            if Path(path).exists() or self._which(path):
                self._llama_executable = path
                break
        
        if not self._llama_executable:
            print("[LLMClient] Warning: llama.cpp executable not found")
    
    def _which(self, program: str) -> Optional[str]:
        """Find executable in PATH."""
        import shutil
        return shutil.which(program)
    
    def _init_huggingface(self):
        """Initialize HuggingFace transformers."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            import torch
            
            self._hf_pipeline = pipeline(
                "text-generation",
                model=self.config.model_path or self.config.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
        except ImportError:
            print("[LLMClient] HuggingFace transformers not available")
            self.config.backend = LLMBackend.PLACEHOLDER
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GENERATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response từ LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Override generation params
        
        Returns:
            LLMResponse
        """
        
        start_time = time.time()
        
        try:
            if self.config.backend == LLMBackend.PLACEHOLDER:
                response = self._generate_placeholder(prompt)
            elif self.config.backend == LLMBackend.LLAMA_CPP:
                response = self._generate_llama_cpp(prompt, system_prompt, **kwargs)
            elif self.config.backend == LLMBackend.OPENROUTER:
                response = self._generate_openrouter(prompt, system_prompt, **kwargs)
            elif self.config.backend == LLMBackend.OPENAI:
                response = self._generate_openai(prompt, system_prompt, **kwargs)
            elif self.config.backend == LLMBackend.GEMINI:
                response = self._generate_gemini(prompt, system_prompt, **kwargs)
            elif self.config.backend == LLMBackend.HUGGINGFACE:
                response = self._generate_huggingface(prompt, system_prompt, **kwargs)
            else:
                response = self._generate_placeholder(prompt)
            
            response.latency_ms = (time.time() - start_time) * 1000
            return response
            
        except Exception as e:
            return LLMResponse(
                text="",
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000
            )
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Streaming generation cho demo mode.
        
        Yields:
            Text chunks as they are generated
        """
        
        if self.config.backend == LLMBackend.OPENROUTER:
            yield from self._stream_openrouter(prompt, system_prompt, **kwargs)
        elif self.config.backend == LLMBackend.OPENAI:
            yield from self._stream_openai(prompt, system_prompt, **kwargs)
        else:
            # Fallback: generate full then yield
            response = self.generate(prompt, system_prompt, **kwargs)
            yield response.text
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BACKEND IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _generate_placeholder(self, prompt: str) -> LLMResponse:
        """Placeholder response cho testing."""
        return LLMResponse(
            text=json.dumps({
                "answer": "[Placeholder] Đây là câu trả lời placeholder cho mục đích testing.",
                "citations": [],
                "abstain": False,
                "reason": None
            }, ensure_ascii=False),
            finish_reason="placeholder",
            tokens_used=0
        )
    
    def _generate_llama_cpp(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate using llama.cpp."""
        
        if not self._llama_executable or not self.config.model_path:
            return self._generate_placeholder(prompt)
        
        # Build full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Build command
        cmd = [
            self._llama_executable,
            "-m", self.config.model_path,
            "-p", full_prompt,
            "-n", str(kwargs.get("max_tokens", self.config.max_tokens)),
            "--temp", str(kwargs.get("temperature", self.config.temperature)),
            "--top-p", str(kwargs.get("top_p", self.config.top_p)),
            "--ctx-size", str(self.config.context_length),
            "-ngl", str(self.config.n_gpu_layers),
            "-t", str(self.config.n_threads),
            "--no-display-prompt"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
            )
            
            return LLMResponse(
                text=result.stdout.strip(),
                finish_reason="stop" if result.returncode == 0 else "error",
                error=result.stderr if result.returncode != 0 else None
            )
            
        except subprocess.TimeoutExpired:
            return LLMResponse(
                text="",
                finish_reason="timeout",
                error="Generation timed out"
            )
    
    def _generate_openrouter(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate using OpenRouter API."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        body = json.dumps({
            "model": kwargs.get("model", self.config.model_name),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }).encode()
        
        req = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/legal-chatbot",
            "X-Title": "Legal Chatbot"
        })
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as r:
                resp = json.loads(r.read())
                
                content = resp["choices"][0]["message"]["content"]
                usage = resp.get("usage", {})
                
                return LLMResponse(
                    text=content,
                    finish_reason=resp["choices"][0].get("finish_reason", "stop"),
                    tokens_used=usage.get("total_tokens", 0),
                    raw_response=resp
                )
                
        except urllib.error.HTTPError as e:
            return LLMResponse(
                text="",
                error=f"HTTP Error: {e.code} - {e.read().decode()}"
            )
        except urllib.error.URLError as e:
            return LLMResponse(
                text="",
                error=f"URL Error: {e.reason}"
            )
    
    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate using OpenAI API."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        url = self.config.api_base_url or "https://api.openai.com/v1/chat/completions"
        body = json.dumps({
            "model": kwargs.get("model", self.config.model_name),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }).encode()
        
        req = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        })
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as r:
                resp = json.loads(r.read())
                
                content = resp["choices"][0]["message"]["content"]
                usage = resp.get("usage", {})
                
                return LLMResponse(
                    text=content,
                    finish_reason=resp["choices"][0].get("finish_reason", "stop"),
                    tokens_used=usage.get("total_tokens", 0),
                    raw_response=resp
                )
                
        except Exception as e:
            return LLMResponse(text="", error=str(e))
    
    def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate using Google Gemini API."""
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model_name}:generateContent?key={self.config.api_key}"
        body = json.dumps({
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
            }
        }).encode()
        
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json"
        })
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as r:
                resp = json.loads(r.read())
                
                content = resp["candidates"][0]["content"]["parts"][0]["text"]
                
                return LLMResponse(
                    text=content,
                    finish_reason="stop",
                    raw_response=resp
                )
                
        except Exception as e:
            return LLMResponse(text="", error=str(e))
    
    def _generate_huggingface(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate using HuggingFace Transformers."""
        
        if not hasattr(self, '_hf_pipeline'):
            return self._generate_placeholder(prompt)
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            outputs = self._hf_pipeline(
                full_prompt,
                max_new_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                do_sample=True,
                return_full_text=False
            )
            
            return LLMResponse(
                text=outputs[0]["generated_text"],
                finish_reason="stop"
            )
            
        except Exception as e:
            return LLMResponse(text="", error=str(e))
    
    def _stream_openrouter(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Streaming from OpenRouter."""
        
        # OpenRouter supports SSE streaming
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        body = json.dumps({
            "model": kwargs.get("model", self.config.model_name),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True
        }).encode()
        
        req = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        })
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as r:
                for line in r:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            yield f"[Error: {e}]"
    
    def _stream_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Streaming from OpenAI."""
        # Similar to OpenRouter
        yield from self._stream_openrouter(prompt, system_prompt, **kwargs)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about current backend."""
        return {
            "backend": self.config.backend.value,
            "mode": self.config.mode.value,
            "model": self.config.model_name or self.config.model_path,
            "context_length": self.config.context_length,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if LLM is available and working."""
        
        test_prompt = "Trả về JSON: {\"status\": \"ok\"}"
        
        start_time = time.time()
        response = self.generate(test_prompt, max_tokens=50)
        latency = (time.time() - start_time) * 1000
        
        return {
            "healthy": response.error is None,
            "backend": self.config.backend.value,
            "latency_ms": latency,
            "error": response.error
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_dev_client() -> LLMClient:
    """Create LLM client optimized for development."""
    config = LLMConfig(
        mode=LLMMode.DEV,
        max_tokens=256,
        context_length=2048,
        temperature=0.1,
        enable_streaming=False
    )
    return LLMClient(config)


def create_demo_client() -> LLMClient:
    """Create LLM client optimized for demo/production."""
    config = LLMConfig(
        mode=LLMMode.DEMO,
        max_tokens=512,
        context_length=4096,
        temperature=0.1,
        enable_streaming=True
    )
    return LLMClient(config)


def create_client_from_env() -> LLMClient:
    """Create client from environment variables."""
    return LLMClient()

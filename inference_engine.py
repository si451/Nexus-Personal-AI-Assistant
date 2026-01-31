import os
import time
from typing import List, Optional, Any, Dict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration

# AirLLM Wrapper

class AirLLMWrapper(BaseChatModel):
    """
    Custom LangChain Wrapper for AirLLM.
    Allows running large models on low VRAM (4GB) using layer-wise inference.
    """
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    model: Any = None
    tokenizer: Any = None

    @property
    def _llm_type(self) -> str:
        return "airllm"
    
    def __init__(self, model_id="Qwen/Qwen2.5-7B-Instruct", **kwargs):
        super().__init__(**kwargs)
        self.model_id = model_id
        
        try:
            from airllm import AutoModel
        except ImportError as e:
            raise ImportError(f"Could not import airllm. Please install it with `pip install airllm`. Error: {e}")

        print(f"[AirLLM] Initializing {self.model_id}...")
        # compression='4bit' uses 4-bit quantization for weights
        self.model = AutoModel.from_pretrained(self.model_id, compression='4bit')
        
        # AirLLM's AutoModel bundles its own tokenizer
        self.tokenizer = self.model.tokenizer
        print("[AirLLM] Model loaded successfully.")

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        # 1. Convert LangChain Messages to Prompt
        prompt = self._convert_messages_to_prompt(messages)
        
        # 2. Tokenize - AirLLM expects input_ids on CPU, it handles device internally
        input_tokens = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False, truncation=True, max_length=2048)
        input_ids = input_tokens['input_ids']
        
        # 3. Generate (AirLLM specific - simpler API)
        print(f"[AirLLM] Generating response for input length {len(input_ids[0])}...")
        start_time = time.time()
        
        # AirLLM's generate returns output_ids directly (not a dict)
        generation_output = self.model.generate(
            input_ids, 
            max_new_tokens=256,
            use_cache=True,
        )
        
        # 4. Decode - generation_output is the full sequence including input
        # It's a tensor of shape [1, seq_len]
        if hasattr(generation_output, 'sequences'):
            output_tokens = generation_output.sequences[0]
        else:
            output_tokens = generation_output[0]
        
        # Remove input tokens from output
        new_tokens = output_tokens[len(input_ids[0]):]
        response_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        end_time = time.time()
        print(f"[AirLLM] Generation finished in {end_time - start_time:.2f}s")

        # 5. Return as ChatResult
        message = AIMessage(content=response_text)
        return ChatResult(generations=[ChatGeneration(message=message)])

    bound_tools: List[Any] = []

    def bind_tools(self, tools):
        """
        Store tools to be injected into the system prompt.
        """
        self.bound_tools = tools
        return self

    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """
        Convert messages to Qwen/ChatML format and inject tool definitions.
        """
        formatted_text = ""
        
        # Inject tools into System Message
        tools_instruction = ""
        if self.bound_tools:
            tools_instruction = "\n\n## Available Tools\n"
            for t in self.bound_tools:
                # Handle both LangChain tools and Pydantic models
                name = getattr(t, 'name', str(t))
                desc = getattr(t, 'description', "")
                args = getattr(t, 'args', {})
                tools_instruction += f"- {name}: {desc}. Args: {args}\n"
            
            tools_instruction += "\n## Tool Usage Format\nTo use a tool, output a JSON block:\n```json\n{\"name\": \"tool_name\", \"parameters\": {\"arg\": \"value\"}}\n```\n"

        for msg in messages:
            content = msg.content
            if isinstance(msg, SystemMessage):
                content += tools_instruction
                formatted_text += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif isinstance(msg, HumanMessage):
                formatted_text += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif isinstance(msg, AIMessage):
                formatted_text += f"<|im_start|>assistant\n{content}<|im_end|>\n"
                
        if not formatted_text: # Fallback if no system message
             formatted_text += f"<|im_start|>system\nYou are a helpful assistant.\n{tools_instruction}<|im_end|>\n"
        
        formatted_text += "<|im_start|>assistant\n"
        return formatted_text

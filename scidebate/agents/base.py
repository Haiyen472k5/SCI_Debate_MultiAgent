"""Abstract Agent — logic chung cho mọi agent trong debate.

BaseAgent compose 3 thứ:
    - LLM backend (gọi model)
    - Memory (lưu lịch sử hội thoại)
    - System prompt (định nghĩa vai trò)
"""

from abc import ABC
from scidebate.llms import BaseLLM, LLMResponse
from scidebate.memory import BaseMemory, ChatHistoryMemory

class BaseAgent(ABC):
    """Abstract debate agent.

    Lifecycle:
        1. __init__: set llm, memory, system prompt
        2. respond(user_message): gọi LLM với memory + message mới
        3. Memory tự động cập nhật sau mỗi lượt
    """

    # Subclass override 2 thuoc tính này
    name: str = "BaseAgent"
    system_prompt: str = ""

    def __init__(self, llm: BaseLLM, memory: BaseMemory = None):
        self.llm = llm
        self.memory = memory if memory is not None else ChatHistoryMemory()

        # Khởi tạo memory với system prompt
        if self.system_prompt:
            self.memory.add("system", self.system_prompt)
        
    def respond(self, user_message: str, **llm_kwargs) -> str:
        """ Sinh response cho user_message, đồng thời cập nhật memory. 

        Args:
            user_message: nội dung lượt prompt 
            llm_kwargs: override temperature, max_tokens cho lượt này

        Returns:
            content của response
        """
        # Thêm user message vào memory
        self.memory.add("user", user_message)

        # Lấy messages từ memory để gọi LLM
        messages = self.memory.get_messages()

        # Gọi LLM để sinh response
        llm_response: LLMResponse = self.llm.generate(messages, **llm_kwargs)

        # Thêm assistant response vào memory
        self.memory.add("assistant", llm_response.content)

        return llm_response.content


    def reset(self) -> None:
        """ reset memory về trạng thái ban đầu (chỉ giữ system prompt) """
        self.memory.clear()
        if self.system_prompt:
            self.memory.add("system", self.system_prompt)

    """
    Công dụng: Trả về string mô tả agent (dùng khi in ra hoặc debug)
    """
    def __repr__(self):
        return f"{self.name}(llm={self.llm}, memory_size={len(self.memory)}))"
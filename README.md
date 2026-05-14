# 🔬 Scientific Debate Simulator

> AI Fact-Checking Assistant for Scientific Literature using Multi-Agent Debate (MAD).

**Course Project** — Modern Topics in Computer Science, UET-VNU, 2025-2026.

## Overview

Scientific Debate Simulator là một hệ thống Multi-Agent Debate dùng LLM để kiểm chứng các tuyên bố khoa học. Hệ thống có 3 agent với vai trò đối lập:

- **🟢 Pro** — bảo vệ claim, đưa ra bằng chứng và lập luận ủng hộ
- **🔴 Con** — phản biện claim, chỉ ra điểm yếu và bằng chứng đối lập  
- **⚖️ Judge** — quan sát toàn bộ debate, đưa ra verdict cuối cùng

Mô hình dựa trên ý tưởng: *"unconfident disagreement đưa ra góc nhìn thay thế có giá trị hơn confident agreement"* — Con Agent tồn tại để tránh confirmation bias của Pro.

## Features

- ✅ Multi-agent debate với Pro/Con/Judge persona
- ✅ Backend Ollama local (miễn phí, không cần API key)
- ✅ Demo UI Streamlit
- ✅ CLI runner để chạy batch
- ✅ Modular architecture, dễ extend
- 🚧 *(Phase 2+)* Heter-MAD: mỗi agent dùng LLM khác nhau
- 🚧 *(Phase 2+)* Uncertainty metrics (entropy, disagreement)
- 🚧 *(Phase 3+)* DAR filtering (Nguyen et al. 2026)
- 🚧 *(Phase 4+)* Tool-MAD với RAG cho paper khoa học

## Architecture
``` bash 
scidebate/
├── agents/         # Pro, Con, Judge classes
├── llms/           # LLM backend abstraction (Ollama)
├── memory/         # Chat history
├── prompts.py      # Prompt templates
├── debate.py       # Debate orchestrator
├── protocols/      # (Phase 2+) WR / CR / RA-CR
├── filtering/      # (Phase 3+) DAR
├── uncertainty/    # (Phase 2+) Entropy, disagreement
└── tools/          # (Phase 4+) RAG, search

configs/            # YAML configs (Phase 2+)
data/               # Datasets
experiments/        # CLI runners
tests/              # Unit tests
app.py              # Streamlit demo UI

```

## Requirements

- Python ≥ 3.10
- [Ollama](https://ollama.com/) (free local LLM runtime)
- 8GB RAM (16GB khuyến nghị)
- WSL2 (nếu dùng Windows)

## Installation

``` bash
# 1. Clone repo
git clone https://github.com/<your-username>/SCI_Debate_MultiAgent.git
cd SCI_Debate_MultiAgent

# 2. Tạo conda environment
conda create -n scidebate python=3.10 -y
conda activate scidebate

# 3. Cài project
pip install -e .

# 4. Cài Ollama và pull model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b
```

## Usage

### 1. Web UI (Streamlit)

``` bash
# Terminal 1: chạy Ollama
ollama serve

# Terminal 2: chạy app
streamlit run app.py


Mở trình duyệt tại `http://localhost:8501`, nhập claim và nhấn **Start Debate**.
```
### 2. CLI

``` bash
# Debate với claim mặc định
python experiments/run_demo.py

# Custom claim + lưu JSON
python experiments/run_demo.py \\
    --claim "Coffee reduces risk of type 2 diabetes." \\
    --rounds 2 \\
    --output outputs/coffee.json

Xem all options: `python experiments/run_demo.py --help`
```
### 3. Python API

``` bash
from scidebate import Debate
from scidebate.llms import OllamaLLM

llm = OllamaLLM(model="qwen2.5:3b")
debate = Debate(llm=llm, max_rounds=2)
result = debate.run("Your scientific claim here.")

print(result.summary())
```

## Testing

``` bash
# Unit tests (mỗi module)
python tests/test_llm.py
python tests/test_memory.py
python tests/test_prompts.py
python tests/test_agents.py
python tests/test_debate.py
```
## Configuration

Phase 1 mặc định:
- Model: `qwen2.5:3b` (~2GB, chạy CPU)
- Rounds: 2
- Temperature: 0.0

Đổi model qua flag CLI hoặc UI sidebar.

## Team

- Mai Anh
- Linh  
- Yến

## References

Dự án được xây dựng dựa trên các công trình:

- Liang et al. (2023) — *Encouraging Divergent Thinking in LLMs through Multi-Agent Debate.* [arXiv:2305.19118](https://arxiv.org/abs/2305.19118)
- Du et al. (2024) — *Improving Factuality through Multi-Agent Debate.* ICML.
- Chan et al. (2023) — *ChatEval: Towards Better LLM-based Evaluators.* [arXiv:2308.07201](https://arxiv.org/abs/2308.07201)
- Smit et al. (2024) — *Should we be going MAD?* [arXiv:2311.17371](https://arxiv.org/abs/2311.17371)
- Wu et al. (2025) — *Impact of MAD Protocols.* [arXiv:2511.07784](https://arxiv.org/abs/2511.07784)

## License

Educational use only. Course project at UET-VNU.

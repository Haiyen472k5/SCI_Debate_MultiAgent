"""Streamlit demo UI cho Scientific Debate Simulator.

Chạy:
    streamlit run app.py

Sau đó mở trình duyệt tại http://localhost:8501
"""
import streamlit as st
from scidebate import Debate
from scidebate.llms import OllamaLLM

# ============================================================
# CONFIG TRANG
# ============================================================

st.set_page_config(
    page_title="Scientific Debate Simulator",
    page_icon="⚖️",
    layout="wide",
)

# ============================================================
# SIDEBAR — CẤU HÌNH
# ============================================================

with st.sidebar:
    st.title("⚙️ Debate Configuration")

    model = st.text_input(
        "Ollama Model",
        value="qwen2.5:3b",
        help="Tên model đã được tải về Ollama (ví dụ: qwen2.5:3b, llama3.2:3b, v.v.)"
    )

    max_rounds = st.slider(
        "Number of Rounds",
        min_value = 1,
        max_value = 4,
        value = 2,
        help="Mỗi round = 1 lượt Pro + 1 lượt Con",
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="0 = deterministic, cao = creative",
    )

    max_tokens = st.slider(
        "Max tokens per turn",
        min_value=100,
        max_value=800,
        value=300,
        step=50,
    )

    st.divider()

    st.markdown(
        "**About**\n\n"
        "Scientific Debate Simulator dùng Multi-Agent Debate "
        "với Pro/Con/Judge để kiểm chứng claims khoa học.\n\n"
        "Backend: Ollama local (free).\n\n"
        "*Built by UET-VNU students, 2025-2026.*"
    )

# ============================================================
# MAIN — INPUT & RESULTS
# ============================================================

# Input claim
claim = st.text_area(
    "**Enter a scientific claim to debate:**",
    value="Drinking 8 glasses of water per day is essential for human health.",
    height=80,
    help="Nhập một tuyên bố khoa học. Ví dụ: 'Vitamin C prevents the common cold.'",
)

# Examples (clickable)
with st.expander("💡 Example claims"):
    st.markdown(
        "- *Reinforcement learning always outperforms supervised learning for robotics.*\n"
        "- *Drinking coffee reduces the risk of type 2 diabetes.*\n"
        "- *The human brain only uses 10% of its capacity.*\n"
        "- *Quantum computers can solve all NP-hard problems efficiently.*\n"
        "- *Eating breakfast is the most important meal for weight loss.*"
    )

# Start button
start = st.button("🎬 Start Debate", type="primary", use_container_width=True)

# ============================================================
# CHẠY DEBATE KHI NHẤN NÚT
# ===========================================================

if start:
    if not claim.strip():
        st.error("Please enter a claim to debate.")
        st.stop()
    # Init LLM
    try:
        llm = OllamaLLM(model=model, temperature=temperature, max_tokens=max_tokens)

    except Exception as e:
        st.error(f"Cannot connect to Ollama. Is `ollama serve` running?\n\nError: {e}")
        st.stop()
    
    # Init Debate
    debate = Debate(llm=llm, max_rounds=max_rounds, verbose=False)

    st.divider()
    st.subheader("⚖️ Debate in progress...")

    # Placeholder để stream từng turn
    transcript_container = st.container()
    spinner_placeholder = st.empty()

    with spinner_placeholder, st.spinner(f"Running debate ({max_rounds} rounds + 1 verdict)... This may take a few minutes on CPU."):
        try:
            result = debate.run(claim)
        except Exception as e:
            st.error(f"Debate failed: {e}")
            st.stop()

    spinner_placeholder.empty()

    # Render transcript
    with transcript_container:
        for turn in result.transcript:
            speaker_icon = "🟢" if turn.speaker == "PRO" else "🔴"
            with st.chat_message(
                "user" if turn.speaker == "PRO" else "assistant",
                avatar="🟢" if turn.speaker == "PRO" else "🔴",
            ):
                st.markdown(f"**{speaker_icon} {turn.speaker} — Round {turn.round_num}**")
                st.markdown(turn.content)

    # Render verdict
    st.divider()
    st.subheader("⚖️ Final Verdict")

    if result.verdict is None:
        st.warning("No verdict produced.")
    else:
        v = result.verdict

        # Color theo verdict
        color_map = {
            "SUPPORTED": "🟢",
            "REFUTED": "🔴",
            "INCONCLUSIVE": "🟡",
        }
        icon = color_map.get(v.verdict, "⚪")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="Verdict", value=f"{icon} {v.verdict}")
            st.metric(label="Confidence", value=f"{v.confidence:.2f}")
        with col2:
            st.markdown("**Justification:**")
            st.info(v.justification)

        # Raw output (debug, collapsed)
        with st.expander("🔍 Raw Judge output (debug)"):
            st.code(v.raw_output)

    st.success(f"Debate completed in {result.num_rounds} round(s).")
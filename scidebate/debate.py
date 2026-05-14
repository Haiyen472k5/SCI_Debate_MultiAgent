"""Debate orchestrator.

Điều phối Pro/Con/Judge qua các round, ghi lại transcript,
và trả về DebateResult với verdict cuối.

Phase 1 protocol (sequential):
    Round 1: Pro opening → Con opening
    Round 2..N: Pro rebuttal → Con rebuttal
    Final: Judge sees full transcript → verdict
"""

from dataclasses import dataclass, field
from scidebate.llms import BaseLLM
from scidebate.agents import ProAgent, ConAgent, JudgeAgent, Verdict
from scidebate.prompts import (
    pro_opening_prompt,
    con_opening_prompt,
    pro_rebuttal_prompt,
    con_rebuttal_prompt,
    judge_verdict_prompt,
)

@dataclass
class Turn:
    """Một lượt phát biểu trong debate."""
    round_num: int
    speaker: str # "PRO" | "CON"
    content: str

    def __str__(self):
        return f"[Round {self.round_num}] {self.speaker}:\n{self.content}"

@dataclass
class DebateResult:
    """Kết quả cuối cùng của debate."""
    claim: str
    transcript: list[Turn] = field(default_factory=list)
    verdict: Verdict = None
    num_rounds: int = 0

    def to_text(self) -> str:
        """Format transcript thành text cho Judge đọc."""
        return "\n\n".join(str(turn) for turn in self.transcript)
    
    def summary(self) -> str:
        """Tóm tắt ngắn cho hiển thị."""
        if not self.verdict:
            return f"Claim: {self.claim}\nNo verdict yet. Rounds: {self.num_rounds}"

        return (
            f"Claim: {self.claim}\n"
            f"Verdict: {self.verdict.verdict} (confidence={self.verdict.confidence:.2f})\n"
            f"Justification: {self.verdict.justification}\n"
            f"Rounds: {self.num_rounds}"
        )

class Debate:
    """Multi-Agent Debate orchestrator.

    Usage:
        debate = Debate(llm=OllamaLLM(...), max_rounds=2)
        result = debate.run("Vitamin C prevents the common cold.")
        print(result.summary())

    Phase 1 dùng cùng 1 LLM cho cả Pro/Con/Judge.
    Phase 2 (Heter-MAD) sẽ cho phép Pro/Con/Judge dùng LLM khác nhau.
    """

    def __init__(
        self, 
        llm: BaseLLM,
        max_rounds: int = 2,
        verbose: bool = True
    ):
        """
        Args:
            llm: LLM backend dùng cho tất cả agent (Phase 1)
            max_rounds: số round tranh luận (không tính lượt Judge cuối)
            verbose: print log mỗi turn (helpful for demo)
        """
        if max_rounds < 1:
            raise ValueError("max_rounds must be at least 1")

        self.llm = llm
        self.max_rounds = max_rounds
        self.verbose = verbose

    def _log(self, message: str) -> None:
        if self.verbose:
            print(message)

    def run(self, claim: str) -> DebateResult:
        """Chạy 1 cuộc debate trên claim, trả về DebateResult.

        Args:
            claim: tuyên bố khoa học cần kiểm chứng

        Returns:
            DebateResult với transcript đầy đủ + verdict
        """
        # 1. Init agents (mỗi lần run là agent mới, memory sạch)
        pro = ProAgent(llm=self.llm)
        con = ConAgent(llm=self.llm)
        judge = JudgeAgent(llm=self.llm)

        result = DebateResult(claim=claim)

        # 2. Round 1: opening statements
        self._log(f"\n{'=' * 60}\nDEBATE: {claim}\n{'=' * 60}")
        self._log("\n----- Round 1: Opening -----")

        # Pro opening
        pro_opening = pro.respond(pro_opening_prompt(claim))
        result.transcript.append(Turn(1, "PRO", pro_opening))
        self._log(f"\nPRO opening:\n{pro_opening}")

        # Con opening
        con_opening = con.respond(con_opening_prompt(claim, pro_opening))
        result.transcript.append(Turn(1, "CON", con_opening))
        self._log(f"\nCON opening:\n{con_opening}")

        # 3. Round 2..N: rebuttals
        last_pro = pro_opening
        last_con = con_opening
        for round_num in range(2, self.max_rounds + 1):
            self._log(f"\n----- Round {round_num}: Rebuttals -----")

            # Pro rebuttal
            pro_rebut = pro.respond(pro_rebuttal_prompt(claim, last_con))
            result.transcript.append(Turn(round_num, "PRO", pro_rebut))
            self._log(f"\nPRO rebuttal:\n{pro_rebut}")
            last_pro = pro_rebut

            # Con rebuttal
            con_rebut = con.respond(con_rebuttal_prompt(claim, last_pro))
            result.transcript.append(Turn(round_num, "CON", con_rebut))
            self._log(f"\nCON rebuttal:\n{con_rebut}")
            last_con = con_rebut
        
        result.num_rounds = self.max_rounds

        # 4. Judge verdict
        self._log(f"\n----- Final Verdict -----")
        transcript_text = result.to_text()
        judge_raw = judge.respond(judge_verdict_prompt(claim, transcript_text))
        verdict = judge.parse_verdict(judge_raw)
        result.verdict = verdict

        self._log(f"\nJudge raw response:\n{judge_raw}")
        self._log(f"\n{'=' * 60}\nFINAL VERDICT: {verdict.verdict} "
                  f"(confidence={verdict.confidence:.2f})\n{'=' * 60}")

        return result

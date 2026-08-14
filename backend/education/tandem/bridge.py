class TandemBridge:
    """Produces public prompts only; private memories are deliberately not accepted."""

    def prepare(self, student_a_id: str, student_b_id: str, topic: str) -> dict[str, dict[str, str]]:
        return {
            student_a_id: {"language": "English", "prompt": "How was your week?", "topic": topic},
            student_b_id: {"language": "Russian", "prompt": "Как прошла твоя неделя?", "topic": topic},
        }

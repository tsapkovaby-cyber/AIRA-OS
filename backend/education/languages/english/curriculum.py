from backend.education.domain.models import CEFRLevel, CurriculumUnit

ENGLISH_UNITS = (
    CurriculumUnit(CEFRLevel.PRE_A1, "Introductions", ("introduce yourself",), ("hello", "name"), ("I am…",), ("clean greeting",), ("short introduction",), ("/h/ clarity",)),
    CurriculumUnit(CEFRLevel.A1, "Cafe", ("order food", "ask a price", "understand a response"), ("coffee", "please", "how much"), ("I would like…",), ("short cafe dialogue",), ("roleplay ordering",), ("/θ/ in three",)),
    CurriculumUnit(CEFRLevel.A2, "Travel problems", ("describe a problem", "request help"), ("delayed", "booking", "help"), ("Could you…?",), ("travel announcement",), ("ask staff for help",), ("sentence stress",)),
    CurriculumUnit(CEFRLevel.B1, "Technology", ("express and support an opinion",), ("benefit", "concern", "impact"), ("opinion clauses",), ("natural short discussion",), ("discuss AI",), ("rhythm",)),
    CurriculumUnit(CEFRLevel.B2, "Work opinions", ("negotiate nuanced viewpoints",), ("trade-off", "proposal", "outcome"), ("hedging",), ("natural meeting extract",), ("defend a proposal",), ("contrastive stress",)),
)

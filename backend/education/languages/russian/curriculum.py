from backend.education.domain.models import CEFRLevel, CurriculumUnit

RUSSIAN_UNITS = (
    CurriculumUnit(CEFRLevel.PRE_A1, "Introductions", ("greet and say your name",), ("приве́т", "меня́ зову́т"), ("Меня зовут…",), ("clean greeting",), ("short introduction",), ("word stress",)),
    CurriculumUnit(CEFRLevel.A1, "Cafe", ("order a drink", "ask a price"), ("ко́фе", "пожа́луйста", "ско́лько"), ("Мне, пожалуйста…",), ("short cafe dialogue",), ("roleplay ordering",), ("unstressed vowels",)),
    CurriculumUnit(CEFRLevel.A2, "Daily life", ("describe routine and location",), ("рабо́та", "до́ма", "о́бычно"), ("Я живу в…",), ("daily routine",), ("describe your day",), ("sentence stress",)),
    CurriculumUnit(CEFRLevel.B1, "Technology", ("express an opinion",), ("по́льза", "риски", "влия́ние"), ("Я считаю, что…",), ("natural discussion",), ("discuss AI",), ("rhythm",)),
    CurriculumUnit(CEFRLevel.B2, "Work opinions", ("discuss nuanced proposals",), ("компроми́сс", "предложе́ние", "результа́т"), ("softening disagreement",), ("meeting extract",), ("defend a proposal",), ("contrastive stress",)),
)

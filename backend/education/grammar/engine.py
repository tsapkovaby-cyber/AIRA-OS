class GrammarEngine:
    """Communication-first prompts backed only by curated rules."""

    RULES = {
        ("english", "past simple"): ("What did you do yesterday?", "Use the past form for a finished past action."),
        ("russian", "location"): ("Где ты живёшь?", "После «в» for a location the word form changes: Я живу в Лондоне."),
    }

    def teach_in_context(self, language: str, concept: str) -> dict[str, str]:
        value = self.RULES.get((language.casefold(), concept.casefold()))
        if not value:
            return {"status": "uncertain", "message": "I need to verify that rule against an approved reference."}
        return {"status": "verified", "prompt": value[0], "explanation": value[1]}

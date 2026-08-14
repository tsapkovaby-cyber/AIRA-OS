"""Thin Telegram presentation adapter; all teaching remains in EducationAPI."""

from backend.education.api import EducationAPI
from backend.education.domain.models import GoalType


class TelegramEducationAdapter:
    MENU = "AIRA Academy\nEnglish · Russian · My Progress · 5-Minute Practice · Conversation · Vocabulary Review · Mistakes · Lesson"

    def __init__(self, api: EducationAPI):
        self.api = api

    def handle_learn(self, platform_user_id: str) -> str:
        profile = self.api.repository.find_by_platform_user(platform_user_id)
        if not profile:
            return "Hi! I'm AIRA. Before we start, I'd like to understand how you want to use the language. Tell me your native language, target language, goal, experience, lesson length, interests, and speaking confidence."
        return self.MENU

    def onboard(self, platform_user_id: str, native_language: str, target_language: str, goal: GoalType, **preferences):
        return self.api.create_student(platform_user_id, native_language, target_language, goal, **preferences)

"""Learner-scoped persistence boundary.

Every read requires the platform owner ID. This makes accidental cross-student
reads fail closed rather than relying on callers to filter shared collections.
"""

from __future__ import annotations

from backend.education.domain.models import LearningMemory, StudentProfile


class StudentAccessDenied(PermissionError):
    pass


class InMemoryStudentRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, StudentProfile] = {}
        self._platform_index: dict[str, str] = {}
        self._memory: dict[str, LearningMemory] = {}

    def create(self, profile: StudentProfile) -> StudentProfile:
        if profile.platform_user_id in self._platform_index:
            raise ValueError("a student already exists for this platform user")
        self._profiles[profile.student_id] = profile
        self._platform_index[profile.platform_user_id] = profile.student_id
        self._memory[profile.student_id] = LearningMemory(profile.student_id)
        return profile

    def find_by_platform_user(self, platform_user_id: str) -> StudentProfile | None:
        student_id = self._platform_index.get(platform_user_id)
        return self._profiles.get(student_id) if student_id else None

    def get(self, student_id: str, platform_user_id: str) -> StudentProfile:
        profile = self._profiles.get(student_id)
        if profile is None or profile.platform_user_id != platform_user_id:
            raise StudentAccessDenied("student data access denied")
        return profile

    def memory(self, student_id: str, platform_user_id: str) -> LearningMemory:
        self.get(student_id, platform_user_id)
        return self._memory[student_id]

    def delete_for_platform_user(self, platform_user_id: str) -> bool:
        student_id = self._platform_index.pop(platform_user_id, None)
        if not student_id:
            return False
        self._profiles.pop(student_id, None)
        self._memory.pop(student_id, None)
        return True

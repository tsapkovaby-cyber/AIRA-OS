from backend.education.domain.models import CurriculumUnit, LessonPlan, LearningMemory, StudentProfile


class LessonEngine:
    DURATIONS = {5, 15, 20, 30, 45, 60}

    def create(self, student: StudentProfile, unit: CurriculumUnit, memory: LearningMemory, *, duration: int | None = None, difficulty: float = .3) -> LessonPlan:
        duration = duration or student.preferred_lesson_duration
        if duration not in self.DURATIONS:
            raise ValueError("unsupported lesson duration")
        review = [item.word for item in sorted(memory.vocabulary, key=lambda item: item.next_review)[:3]]
        speaking = list(unit.speaking)
        listening = list(unit.listening)
        if duration == 5:
            speaking = [f"Mini dialogue: {unit.speaking[0]}", "Active recall: How would you say it?"]
            listening = [unit.listening[0]]
        return LessonPlan(student.student_id, unit.level, unit.topic, list(unit.objectives), list(unit.vocabulary), list(unit.grammar), speaking, listening, list(unit.pronunciation), review, duration, difficulty)

    def finish(self, plan: LessonPlan, memory: LearningMemory, *, speaking_minutes: int, performance: float) -> dict[str, object]:
        memory.lesson_history.append({"lesson_id": plan.lesson_id, "topic": plan.topic, "duration": plan.estimated_duration, "performance": performance})
        progress = memory.progress
        progress.lessons_completed += 1
        progress.learning_minutes += plan.estimated_duration
        progress.speaking_minutes += speaking_minutes
        return {"duration": plan.estimated_duration, "speaking_time": speaking_minutes, "new_words": plan.target_vocabulary, "mistakes": len(memory.mistakes), "review_items": plan.review_items, "next_lesson_recommendation": "Continue with active conversation and due review."}

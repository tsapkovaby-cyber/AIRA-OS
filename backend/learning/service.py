"""Application facade and deterministic progress engine."""
from __future__ import annotations
from datetime import date, timedelta
from .models import Course, CourseProgress, Enrollment, ExerciseResult, LearningPath, LearningProfile, LearningStatus, Student, new_id
from .ports import FakeTutor, InMemoryLearningMemory, LearningMemoryPort, TutorPort
class LearningError(ValueError): pass
class NotFound(LearningError): pass
class DuplicateEnrollment(LearningError): pass
class PrerequisiteNotMet(LearningError): pass
class LearningPlatformService:
    def __init__(self, *, tutor: TutorPort|None=None, memory: LearningMemoryPort|None=None)->None:
        self.students={}; self.profiles={}; self.courses={}; self.enrollments={}; self.results=[]; self.tutor=tutor or FakeTutor(); self.memory=memory or InMemoryLearningMemory()
    def create_student(self)->Student:
        s=Student(); self.students[s.id]=s; return s
    def get_student(self, student_id): return self._student(student_id)
    def update_profile(self, profile:LearningProfile): self._student(profile.student_id); self.profiles[profile.student_id]=profile; return profile
    create_or_update_learning_profile=update_profile
    def create_course(self, course:Course): self.courses[course.id]=course; return course
    def get_course(self, course_id): return self._course(course_id)
    def enroll(self, student_id, course_id):
        self._student(student_id); self._course(course_id); key=(student_id,course_id)
        if key in self.enrollments: raise DuplicateEnrollment("student already enrolled")
        e=Enrollment(new_id(),student_id,course_id); self.enrollments[key]=e; return e
    enroll_student=enroll
    def get_enrollment(self, student_id, course_id): return self._context(student_id,course_id)[0]
    def get_learning_path(self, student_id, course_id):
        e,c=self._context(student_id,course_id); ids=[l.id for l in c.ordered_lessons() if l.id not in e.completed_lesson_ids and set(l.prerequisite_lesson_ids).issubset(e.completed_lesson_ids)]; return LearningPath(student_id,course_id,ids)
    def start_lesson(self, student_id, course_id, lesson_id):
        e,c=self._context(student_id,course_id); l=self._lesson(c,lesson_id)
        if not set(l.prerequisite_lesson_ids).issubset(e.completed_lesson_ids): raise PrerequisiteNotMet(lesson_id)
        e.started_lesson_ids.add(lesson_id); e.status=LearningStatus.IN_PROGRESS; self._touch(e); return e
    def complete_lesson(self, student_id, course_id, lesson_id):
        e,c=self._context(student_id,course_id); self._lesson(c,lesson_id)
        if lesson_id not in e.started_lesson_ids: raise LearningError("lesson must be started before completion")
        e.completed_lesson_ids.add(lesson_id)
        if len(e.completed_lesson_ids)==len(c.ordered_lessons()): e.status=LearningStatus.COMPLETED
        self._touch(e); self.memory.remember(student_id,"completed_lessons",lesson_id); return e
    def submit_exercise_result(self, result:ExerciseResult):
        _,c=self._context(result.student_id,result.course_id); l=self._lesson(c,result.lesson_id)
        if not any(x.id==result.exercise_id for x in l.exercises): raise NotFound(result.exercise_id)
        if not 0<=result.score<=1: raise LearningError("score must be between 0 and 1")
        self.results.append(result); return result
    def progress(self, student_id, course_id):
        e,c=self._context(student_id,course_id); lessons=c.ordered_lessons(); scores={}
        for r in self.results:
            if r.student_id==student_id and r.course_id==course_id and r.topic: scores.setdefault(r.topic,[]).append(r.score)
        av={k:sum(v)/len(v) for k,v in scores.items()}; pct=round((len(e.completed_lesson_ids)/len(lessons)*100) if lessons else 0,2)
        return CourseProgress(course_id,len(e.completed_lesson_ids),len(lessons),pct,sorted(k for k,v in av.items() if v>=.8),sorted(k for k,v in av.items() if v<.6),e.streak_days)
    get_course_progress=progress
    def next_lesson(self, student_id, course_id):
        e,c=self._context(student_id,course_id)
        for l in c.ordered_lessons():
            if l.id not in e.completed_lesson_ids and set(l.prerequisite_lesson_ids).issubset(e.completed_lesson_ids): return l
        return None
    get_next_recommended_lesson=next_lesson
    def start_tutor_session(self, student_id, *, mode, lesson_id=None): return self.tutor.start_session(self._student(student_id),mode=mode,lesson_id=lesson_id)
    @staticmethod
    def _touch(e):
        today=date.today(); previous=date.fromisoformat(e.last_activity_date) if e.last_activity_date else None
        if previous==today: return
        e.streak_days = e.streak_days+1 if previous==today-timedelta(days=1) else 1; e.last_activity_date=today.isoformat()
    def _student(self,i):
        try:return self.students[i]
        except KeyError:raise NotFound(i) from None
    def _course(self,i):
        try:return self.courses[i]
        except KeyError:raise NotFound(i) from None
    def _context(self,s,c):
        self._student(s); course=self._course(c)
        try:return self.enrollments[(s,c)],course
        except KeyError:raise NotFound("enrollment") from None
    @staticmethod
    def _lesson(c,i):
        for l in c.ordered_lessons():
            if l.id==i:return l
        raise NotFound(i)

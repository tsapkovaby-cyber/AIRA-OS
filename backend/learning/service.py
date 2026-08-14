"""Application facade and deterministic progress engine."""
from __future__ import annotations
from datetime import date, timedelta
from .models import Course, CourseProgress, Enrollment, ExerciseResult, LearningPath, LearningProfile, LearningStatus, Student, new_id
from .path import build_learning_path_snapshot
from .ports import FakeTutor, InMemoryLearningMemory, LearningMemoryPort, TutorPort
from .personalization import PersonalizationEngine
from .placement import PlacementAnswer, PlacementAssessment, PlacementResult, reference_cefr_placement
class LearningError(ValueError): pass
class NotFound(LearningError): pass
class DuplicateEnrollment(LearningError): pass
class PrerequisiteNotMet(LearningError): pass
class LearningPlatformService:
    def __init__(self,*,tutor:TutorPort|None=None,memory:LearningMemoryPort|None=None)->None:
        self.students:dict[str,Student]={};self.profiles:dict[str,LearningProfile]={};self.courses:dict[str,Course]={};self.enrollments:dict[tuple[str,str],Enrollment]={};self.results:list[ExerciseResult]=[];self.placement_results:dict[tuple[str,str],PlacementResult]={};self.tutor=tutor or FakeTutor();self.memory=memory or InMemoryLearningMemory();self.personalization=PersonalizationEngine(self.memory)
    def create_student(self)->Student:
        student=Student();self.students[student.id]=student;return student
    def get_student(self,student_id:str)->Student:return self._student(student_id)
    def update_profile(self,profile:LearningProfile)->LearningProfile:
        self._student(profile.student_id);self.profiles[profile.student_id]=profile;return profile
    create_or_update_learning_profile=update_profile
    def create_course(self,course:Course)->Course:self.courses[course.id]=course;return course
    def get_course(self,course_id:str)->Course:return self._course(course_id)
    def enroll(self,student_id:str,course_id:str)->Enrollment:
        self._student(student_id);self._course(course_id);key=(student_id,course_id)
        if key in self.enrollments:raise DuplicateEnrollment("student already enrolled")
        enrollment=Enrollment(new_id(),student_id,course_id);self.enrollments[key]=enrollment;return enrollment
    enroll_student=enroll
    def get_enrollment(self,student_id:str,course_id:str)->Enrollment:return self._context(student_id,course_id)[0]
    def get_learning_path(self,student_id:str,course_id:str)->LearningPath:
        enrollment,course=self._context(student_id,course_id);ids=[lesson.id for lesson in course.ordered_lessons() if lesson.id not in enrollment.completed_lesson_ids and set(lesson.prerequisite_lesson_ids).issubset(enrollment.completed_lesson_ids)];return LearningPath(student_id,course_id,ids)
    def learning_path_snapshot(self,student_id:str,course_id:str):
        enrollment,course=self._context(student_id,course_id);return build_learning_path_snapshot(enrollment,course)
    def start_lesson(self,student_id:str,course_id:str,lesson_id:str)->Enrollment:
        enrollment,course=self._context(student_id,course_id);lesson=self._lesson(course,lesson_id)
        if not set(lesson.prerequisite_lesson_ids).issubset(enrollment.completed_lesson_ids):raise PrerequisiteNotMet(lesson_id)
        enrollment.started_lesson_ids.add(lesson_id);enrollment.status=LearningStatus.IN_PROGRESS;self._touch(enrollment);return enrollment
    def complete_lesson(self,student_id:str,course_id:str,lesson_id:str)->Enrollment:
        enrollment,course=self._context(student_id,course_id);self._lesson(course,lesson_id)
        if lesson_id not in enrollment.started_lesson_ids:raise LearningError("lesson must be started before completion")
        enrollment.completed_lesson_ids.add(lesson_id)
        if len(enrollment.completed_lesson_ids)==len(course.ordered_lessons()):enrollment.status=LearningStatus.COMPLETED
        self._touch(enrollment);self.memory.remember(student_id,"completed_lessons",lesson_id);return enrollment
    def submit_exercise_result(self,result:ExerciseResult)->ExerciseResult:
        _,course=self._context(result.student_id,result.course_id);lesson=self._lesson(course,result.lesson_id)
        if not any(exercise.id==result.exercise_id for exercise in lesson.exercises):raise NotFound(result.exercise_id)
        if not 0<=result.score<=1:raise LearningError("score must be between 0 and 1")
        self.results.append(result);self.personalization.record_result(result);return result
    def record_conversation_issue(self,student_id:str,topic:str)->None:
        self._student(student_id);self.personalization.record_conversation_issue(student_id,topic)
    def learning_insight(self,student_id:str):
        self._student(student_id);return self.personalization.insight(student_id,self.profiles.get(student_id))
    def run_placement(self,student_id:str,target_language:str,answers:list[PlacementAnswer],assessment:PlacementAssessment|None=None)->PlacementResult:
        self._student(student_id);assessment=assessment or reference_cefr_placement();result=assessment.evaluate(student_id,target_language,answers);self.placement_results[(student_id,target_language.casefold())]=result
        profile=self.profiles.get(student_id) or LearningProfile(student_id);profile.current_level=result.level
        if target_language not in profile.target_languages:profile.target_languages.append(target_language)
        self.profiles[student_id]=profile;self.memory.remember(student_id,"placement_levels",f"{target_language}:{result.level}");return result
    def get_placement_result(self,student_id:str,target_language:str)->PlacementResult:
        self._student(student_id)
        try:return self.placement_results[(student_id,target_language.casefold())]
        except KeyError:raise NotFound("placement result") from None
    def recommended_course_for_placement(self,student_id:str,target_language:str):
        result=self.get_placement_result(student_id,target_language);language=target_language.casefold()
        matches=[course for course in self.courses.values() if (course.language or "").casefold()==language and course.level==result.recommended_course_level]
        return matches[0] if matches else None
    def progress(self,student_id:str,course_id:str)->CourseProgress:
        enrollment,course=self._context(student_id,course_id);lessons=course.ordered_lessons();scores:dict[str,list[float]]={}
        for result in self.results:
            if result.student_id==student_id and result.course_id==course_id and result.topic:scores.setdefault(result.topic,[]).append(result.score)
        averages={topic:sum(values)/len(values) for topic,values in scores.items()};pct=round((len(enrollment.completed_lesson_ids)/len(lessons)*100) if lessons else 0,2);return CourseProgress(course_id,len(enrollment.completed_lesson_ids),len(lessons),pct,sorted(k for k,v in averages.items() if v>=.8),sorted(k for k,v in averages.items() if v<.6),enrollment.streak_days)
    get_course_progress=progress
    def next_lesson(self,student_id:str,course_id:str):
        enrollment,course=self._context(student_id,course_id)
        for lesson in course.ordered_lessons():
            if lesson.id not in enrollment.completed_lesson_ids and set(lesson.prerequisite_lesson_ids).issubset(enrollment.completed_lesson_ids):return lesson
        return None
    get_next_recommended_lesson=next_lesson
    def start_tutor_session(self,student_id:str,*,mode:str,lesson_id:str|None=None):return self.tutor.start_session(self._student(student_id),mode=mode,lesson_id=lesson_id)
    @staticmethod
    def _touch(enrollment:Enrollment)->None:
        today=date.today();previous=date.fromisoformat(enrollment.last_activity_date) if enrollment.last_activity_date else None
        if previous==today:return
        enrollment.streak_days=enrollment.streak_days+1 if previous==today-timedelta(days=1) else 1;enrollment.last_activity_date=today.isoformat()
    def _student(self,student_id:str)->Student:
        try:return self.students[student_id]
        except KeyError:raise NotFound(student_id) from None
    def _course(self,course_id:str)->Course:
        try:return self.courses[course_id]
        except KeyError:raise NotFound(course_id) from None
    def _context(self,student_id:str,course_id:str):
        self._student(student_id);course=self._course(course_id)
        try:return self.enrollments[(student_id,course_id)],course
        except KeyError:raise NotFound("enrollment") from None
    @staticmethod
    def _lesson(course:Course,lesson_id:str):
        for lesson in course.ordered_lessons():
            if lesson.id==lesson_id:return lesson
        raise NotFound(lesson_id)

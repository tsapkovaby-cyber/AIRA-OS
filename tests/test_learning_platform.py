import pytest
from backend.learning.models import ExerciseResult, LearningProfile
from backend.learning.seeds import conversational_english_a1
from backend.learning.service import DuplicateEnrollment, LearningError, LearningPlatformService, NotFound, PrerequisiteNotMet

def setup_platform():
    s=LearningPlatformService(); student=s.create_student(); course=s.create_course(conversational_english_a1()); enrollment=s.enroll(student.id,course.id); return s,student,course,enrollment

def test_profile_course_enrollment_and_duplicate_guard():
    s,u,c,_=setup_platform(); p=s.create_or_update_learning_profile(LearningProfile(u.id,native_language="Russian",target_languages=["English"],current_level="A1",target_level="B1")); assert s.get_student(u.id) is u and s.get_course(c.id) is c and p.student_id==u.id
    with pytest.raises(DuplicateEnrollment): s.enroll_student(u.id,c.id)

def test_lesson_prerequisites_progress_path_and_recommendation():
    s,u,c,e=setup_platform(); first,second=c.ordered_lessons(); assert s.get_next_recommended_lesson(u.id,c.id).id==first.id and s.get_learning_path(u.id,c.id).lesson_ids==[first.id]
    with pytest.raises(PrerequisiteNotMet): s.start_lesson(u.id,c.id,second.id)
    s.start_lesson(u.id,c.id,first.id); assert e.streak_days==1; s.complete_lesson(u.id,c.id,first.id); assert e.streak_days==1
    assert s.get_next_recommended_lesson(u.id,c.id).id==second.id and s.get_learning_path(u.id,c.id).lesson_ids==[second.id] and s.get_course_progress(u.id,c.id).completion_percentage==50.0 and s.progress(u.id,c.id).streak_days==1

def test_exercise_results_derive_strengths_and_weaknesses():
    s,u,c,_=setup_platform(); first=c.ordered_lessons()[0]; s.submit_exercise_result(ExerciseResult(u.id,c.id,first.id,first.exercises[0].id,.9,"greetings")); s.submit_exercise_result(ExerciseResult(u.id,c.id,first.id,first.exercises[0].id,.2,"introductions")); p=s.progress(u.id,c.id); assert p.strengths==["greetings"] and p.weaknesses==["introductions"]

def test_invalid_completion_and_score_are_rejected():
    s,u,c,_=setup_platform(); first=c.ordered_lessons()[0]
    with pytest.raises(LearningError): s.complete_lesson(u.id,c.id,first.id)
    with pytest.raises(LearningError): s.submit_exercise_result(ExerciseResult(u.id,c.id,first.id,first.exercises[0].id,2.0))

def test_student_isolation_and_tutor_memory_boundaries():
    s,u,c,_=setup_platform(); other=s.create_student()
    with pytest.raises(NotFound): s.progress(other.id,c.id)
    session=s.start_tutor_session(u.id,mode="text",lesson_id=c.ordered_lessons()[0].id); assert session.student_id==u.id; s.memory.remember(u.id,"mistakes","hello/hi"); assert s.memory.recall(other.id,"mistakes")==[]

def test_reference_course_is_subject_generic_platform_data():
    c=conversational_english_a1(); assert c.subject=="language" and c.language=="English" and len(c.modules)==1 and len(c.ordered_lessons())==2

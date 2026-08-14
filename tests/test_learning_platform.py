import pytest
from backend.learning.models import ExerciseResult, LearningProfile
from backend.learning.seeds import conversational_english_a1, conversational_english_catalog
from backend.learning.service import DuplicateEnrollment, LearningError, LearningPlatformService, NotFound, PrerequisiteNotMet

def setup_platform():
    service=LearningPlatformService();student=service.create_student();course=service.create_course(conversational_english_a1());enrollment=service.enroll(student.id,course.id);return service,student,course,enrollment

def test_profile_course_enrollment_and_duplicate_guard():
    service,student,course,_=setup_platform();profile=service.create_or_update_learning_profile(LearningProfile(student.id,native_language="Russian",target_languages=["English"],current_level="A1",target_level="B1"));assert service.get_student(student.id) is student and service.get_course(course.id) is course and profile.student_id==student.id
    with pytest.raises(DuplicateEnrollment):service.enroll_student(student.id,course.id)

def test_lesson_prerequisites_progress_path_and_recommendation():
    service,student,course,enrollment=setup_platform();first,second=course.ordered_lessons();assert service.get_next_recommended_lesson(student.id,course.id).id==first.id and service.get_learning_path(student.id,course.id).lesson_ids==[first.id]
    with pytest.raises(PrerequisiteNotMet):service.start_lesson(student.id,course.id,second.id)
    service.start_lesson(student.id,course.id,first.id);assert enrollment.streak_days==1;service.complete_lesson(student.id,course.id,first.id);assert enrollment.streak_days==1
    assert service.get_next_recommended_lesson(student.id,course.id).id==second.id and service.get_learning_path(student.id,course.id).lesson_ids==[second.id] and service.get_course_progress(student.id,course.id).completion_percentage==50.0

def test_exercise_results_derive_strengths_and_weaknesses():
    service,student,course,_=setup_platform();first=course.ordered_lessons()[0];service.submit_exercise_result(ExerciseResult(student.id,course.id,first.id,first.exercises[0].id,.9,"greetings"));service.submit_exercise_result(ExerciseResult(student.id,course.id,first.id,first.exercises[0].id,.2,"introductions"));progress=service.progress(student.id,course.id);assert progress.strengths==["greetings"] and progress.weaknesses==["introductions"]

def test_invalid_completion_and_score_are_rejected():
    service,student,course,_=setup_platform();first=course.ordered_lessons()[0]
    with pytest.raises(LearningError):service.complete_lesson(student.id,course.id,first.id)
    with pytest.raises(LearningError):service.submit_exercise_result(ExerciseResult(student.id,course.id,first.id,first.exercises[0].id,2.0))

def test_student_isolation_and_tutor_memory_boundaries():
    service,student,course,_=setup_platform();other=service.create_student()
    with pytest.raises(NotFound):service.progress(other.id,course.id)
    session=service.start_tutor_session(student.id,mode="text",lesson_id=course.ordered_lessons()[0].id);assert session.student_id==student.id;service.memory.remember(student.id,"mistakes","hello/hi");assert service.memory.recall(other.id,"mistakes")==[]

def test_reference_course_catalog_is_a1_through_b2():
    catalog=conversational_english_catalog();assert [course.level for course in catalog]==["A1","A2","B1","B2"] and all(course.subject=="language" for course in catalog)

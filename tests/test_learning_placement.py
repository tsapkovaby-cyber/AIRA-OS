from backend.learning.models import Course
from backend.learning.placement import PlacementAnswer, PlacementAssessment, PlacementQuestion, reference_cefr_placement
from backend.learning.service import LearningPlatformService, NotFound
import pytest


def test_reference_placement_sets_profile_level_and_target_language():
    service = LearningPlatformService()
    student = service.create_student()
    answers = [
        PlacementAnswer("q1", "Hello"),
        PlacementAnswer("q2", "drinks"),
        PlacementAnswer("q3", "contrast"),
    ]
    result = service.run_placement(student.id, "English", answers)
    assert result.level == "B1"
    assert service.profiles[student.id].current_level == "B1"
    assert service.profiles[student.id].target_languages == ["English"]
    assert service.get_placement_result(student.id, "english").level == "B1"


def test_placement_scores_skills_independently():
    assessment = PlacementAssessment([
        PlacementQuestion("g1", "grammar", "A1", "a", "yes"),
        PlacementQuestion("g2", "grammar", "A2", "b", "yes"),
        PlacementQuestion("v1", "vocabulary", "A1", "c", "yes"),
    ])
    result = assessment.evaluate("student", "English", [PlacementAnswer("g1", "yes"), PlacementAnswer("g2", "no"), PlacementAnswer("v1", "yes")])
    assert result.skill_scores == {"grammar": .5, "vocabulary": 1.0}


def test_placement_can_recommend_existing_course_by_language_and_level():
    service = LearningPlatformService()
    student = service.create_student()
    service.create_course(Course("english-b1", "English B1", "language", "B1", language="English"))
    service.run_placement(student.id, "English", [
        PlacementAnswer("q1", "Hello"),
        PlacementAnswer("q2", "drinks"),
        PlacementAnswer("q3", "contrast"),
    ], reference_cefr_placement())
    assert service.recommended_course_for_placement(student.id, "English").id == "english-b1"


def test_placement_results_are_student_scoped():
    service = LearningPlatformService()
    first = service.create_student()
    second = service.create_student()
    service.run_placement(first.id, "English", [PlacementAnswer("q1", "Hello")])
    with pytest.raises(NotFound):
        service.get_placement_result(second.id, "English")

"""Reference learning content; never platform logic."""
from .languages import learning_languages
from .models import Course, CourseModule, Exercise, Lesson

def conversational_english_a1()->Course:
    greeting=Lesson(id="en-a1-greetings",title="Greeting someone",learning_objectives=["Use common greetings"],content="Practice choosing a greeting for the situation.",exercises=[Exercise("en-a1-greet-mc","Choose a greeting","multiple_choice","greetings")])
    introduce=Lesson(id="en-a1-introduce",title="Introducing yourself",learning_objectives=["Say your name","Ask another person's name"],content="Practice a short introduction.",prerequisite_lesson_ids=[greeting.id],exercises=[Exercise("en-a1-intro-prompt","Introduce yourself","conversation_prompt","introductions")])
    return Course(id="conversational-english-a1",title="Conversational English — A1",subject="language",level="A1",language="English",description="Reference course demonstrating the learning-platform architecture.",modules=[CourseModule("en-a1-introductions","Introductions",[greeting,introduce])])

def conversational_english_catalog()->list[Course]:
    a1=conversational_english_a1()
    return [a1]+[Course(id=f"conversational-english-{level.lower()}",title=f"Conversational English — {level}",subject="language",level=level,language="English",description="Reference level placeholder; lessons are authored in later content sprints.") for level in ("A2","B1","B2")]

def multilingual_language_catalog(levels:tuple[str,...]=( "A1","A2","B1","B2","C1","C2"))->list[Course]:
    """Create data-driven course shells for every supported learning language."""
    courses:list[Course]=[]
    for language in learning_languages():
        for level in levels:
            slug=f"{language.code}-{level.lower()}"
            courses.append(Course(id=f"language-{slug}",title=f"{language.name} — {level}",subject="language",level=level,language=language.name,description=f"{language.name} learning path at {level}. Content is authored in dedicated curriculum sprints."))
    return courses

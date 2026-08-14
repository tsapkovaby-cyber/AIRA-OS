"""Reference learning content; never platform logic."""
from .models import Course, CourseModule, Exercise, Lesson

def conversational_english_a1()->Course:
    greeting=Lesson(id="en-a1-greetings",title="Greeting someone",learning_objectives=["Use common greetings"],content="Practice choosing a greeting for the situation.",exercises=[Exercise("en-a1-greet-mc","Choose a greeting","multiple_choice","greetings")])
    introduce=Lesson(id="en-a1-introduce",title="Introducing yourself",learning_objectives=["Say your name","Ask another person's name"],content="Practice a short introduction.",prerequisite_lesson_ids=[greeting.id],exercises=[Exercise("en-a1-intro-prompt","Introduce yourself","conversation_prompt","introductions")])
    return Course(id="conversational-english-a1",title="Conversational English — A1",subject="language",level="A1",language="English",description="Reference course demonstrating the learning-platform architecture.",modules=[CourseModule("en-a1-introductions","Introductions",[greeting,introduce])])

def conversational_english_catalog()->list[Course]:
    """Reference level catalog; A2-B2 are placeholders for later content sprints."""
    a1=conversational_english_a1()
    return [a1]+[Course(id=f"conversational-english-{level.lower()}",title=f"Conversational English — {level}",subject="language",level=level,language="English",description="Reference level placeholder; lessons are authored in later content sprints.") for level in ("A2","B1","B2")]

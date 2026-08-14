"""Ports keeping learning logic independent of AI vendors and transports."""
from __future__ import annotations
from typing import Protocol
from .models import Student, TutorSession

class TutorPort(Protocol):
    def start_session(self,student:Student,*,mode:str,lesson_id:str|None=None)->TutorSession: ...
class LearningMemoryPort(Protocol):
    def remember(self,student_id:str,category:str,value:str)->None: ...
    def recall(self,student_id:str,category:str)->list[str]: ...
class FakeTutor:
    def start_session(self,student:Student,*,mode:str,lesson_id:str|None=None)->TutorSession:
        return TutorSession(id=f"tutor-{student.id}-{mode}",student_id=student.id,mode=mode,lesson_id=lesson_id)
class InMemoryLearningMemory:
    def __init__(self)->None:self._items:dict[tuple[str,str],list[str]]={}
    def remember(self,student_id:str,category:str,value:str)->None:self._items.setdefault((student_id,category),[]).append(value)
    def recall(self,student_id:str,category:str)->list[str]:return list(self._items.get((student_id,category),[]))

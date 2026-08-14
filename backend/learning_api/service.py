"""Thin authenticated API/application facade over accounts and learning domains."""
from __future__ import annotations
from dataclasses import asdict
from typing import Any
from backend.accounts.service import AccountService
from backend.learning.models import LearningProfile
from backend.learning.service import LearningPlatformService

class APIError(ValueError): pass
class Unauthorized(APIError): pass
class Forbidden(APIError): pass
class LearningPlatformAPI:
    def __init__(self,accounts:AccountService,learning:LearningPlatformService)->None:self.accounts=accounts;self.learning=learning
    def register(self,email:str,password:str)->dict[str,Any]:
        account,student=self.accounts.register_student_account(email,password,self.learning);return {"account_id":account.id,"student_id":student.id,"status":account.status.value}
    def login(self,email:str,password:str)->dict[str,Any]:
        account,token=self.accounts.authenticate(email,password);return {"account_id":account.id,"session_token":token}
    def logout(self,token:str)->None:self.accounts.logout(token)
    def current_account(self,token:str):
        try:return self.accounts.get_current_account_from_session(token)
        except Exception as exc:raise Unauthorized("invalid session") from exc
    def get_profile(self,token:str)->dict[str,Any]:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);profile=self.learning.profiles.get(student.id);return asdict(profile) if profile else {"student_id":student.id}
    def update_profile(self,token:str,**changes:Any)->dict[str,Any]:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);current=self.learning.profiles.get(student.id) or LearningProfile(student.id)
        allowed={"native_language","target_languages","current_level","target_level","learning_goals","preferred_learning_style","daily_learning_target_minutes","interests"}
        for key,value in changes.items():
            if key not in allowed:raise APIError(f"unsupported profile field: {key}")
            setattr(current,key,value)
        return asdict(self.learning.update_profile(current))
    def list_courses(self,token:str)->list[dict[str,Any]]:
        self.current_account(token);return [{"id":c.id,"title":c.title,"subject":c.subject,"level":c.level,"language":c.language,"description":c.description} for c in self.learning.courses.values()]
    def enroll(self,token:str,course_id:str)->dict[str,Any]:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);enrollment=self.learning.enroll(student.id,course_id);return {"id":enrollment.id,"student_id":student.id,"course_id":course_id,"status":enrollment.status.value}
    def course_progress(self,token:str,course_id:str)->dict[str,Any]:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);return asdict(self.learning.progress(student.id,course_id))
    def next_lesson(self,token:str,course_id:str)->dict[str,Any]|None:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);lesson=self.learning.next_lesson(student.id,course_id);return asdict(lesson) if lesson else None
    def start_lesson(self,token:str,course_id:str,lesson_id:str)->dict[str,Any]:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);enrollment=self.learning.start_lesson(student.id,course_id,lesson_id);return {"course_id":course_id,"lesson_id":lesson_id,"status":enrollment.status.value}
    def complete_lesson(self,token:str,course_id:str,lesson_id:str)->dict[str,Any]:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);enrollment=self.learning.complete_lesson(student.id,course_id,lesson_id);return {"course_id":course_id,"lesson_id":lesson_id,"status":enrollment.status.value}
    def start_tutor_session(self,token:str,mode:str="text",lesson_id:str|None=None)->dict[str,Any]:
        account=self.current_account(token);student=self.accounts.get_primary_student(account.id);return asdict(self.learning.start_tutor_session(student.id,mode=mode,lesson_id=lesson_id))

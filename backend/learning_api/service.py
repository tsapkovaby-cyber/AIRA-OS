"""Thin authenticated API/application facade over accounts and learning domains."""
from __future__ import annotations
from dataclasses import asdict
from typing import Any
from backend.accounts.service import AccountService, AuthenticationFailed
from backend.learning.languages import explanation_languages, learning_languages, resolve_explanation_language
from backend.learning.models import LearningProfile
from backend.learning.service import LearningPlatformService

class APIError(ValueError): pass
class Unauthorized(APIError): pass
class LearningPlatformAPI:
    def __init__(self,accounts:AccountService,learning:LearningPlatformService)->None:self.accounts=accounts;self.learning=learning
    def register(self,email:str,password:str)->dict[str,Any]:
        account=self.accounts.register_student_account(email,password);student=self.learning.create_student();self.accounts.create_student_link(account.id,student.id);return {"account_id":account.id,"student_id":student.id,"status":account.status.value}
    def login(self,email:str,password:str)->dict[str,Any]:
        account,token=self.accounts.authenticate(email,password);return {"account_id":account.id,"session_token":token}
    def logout(self,token:str)->None:self.accounts.logout(token)
    def current_account(self,token:str):
        try:return self.accounts.get_current_account_from_session(token)
        except AuthenticationFailed as exc:raise Unauthorized("invalid session") from exc
    def _student_id(self,token:str)->str:
        account=self.current_account(token);return self.accounts.get_primary_student(account.id)
    def get_profile(self,token:str)->dict[str,Any]:
        student_id=self._student_id(token);profile=self.learning.profiles.get(student_id);data=asdict(profile) if profile else {"student_id":student_id};data["app_language"]=data.get("explanation_language") or data.get("native_language");return data
    def update_profile(self,token:str,**changes:Any)->dict[str,Any]:
        student_id=self._student_id(token);current=self.learning.profiles.get(student_id) or LearningProfile(student_id)
        allowed={"native_language","explanation_language","target_languages","current_level","target_level","learning_goals","preferred_learning_style","daily_learning_target_minutes","interests"}
        for key,value in changes.items():
            if key not in allowed:raise APIError(f"unsupported profile field: {key}")
            setattr(current,key,value)
        current.explanation_language=resolve_explanation_language(current.native_language,current.explanation_language)
        data=asdict(self.learning.update_profile(current));data["app_language"]=current.explanation_language;return data
    def list_languages(self,token:str)->dict[str,Any]:
        self.current_account(token);return {"learning":[asdict(item) for item in learning_languages()],"explanation":[asdict(item) for item in explanation_languages()]}
    def app_language(self,token:str)->str|None:
        profile=self.learning.profiles.get(self._student_id(token));return resolve_explanation_language(profile.native_language,profile.explanation_language) if profile else None
    def list_courses(self,token:str)->list[dict[str,Any]]:
        self.current_account(token);return [{"id":c.id,"title":c.title,"subject":c.subject,"level":c.level,"language":c.language,"description":c.description} for c in self.learning.courses.values()]
    def enroll(self,token:str,course_id:str)->dict[str,Any]:
        student_id=self._student_id(token);enrollment=self.learning.enroll(student_id,course_id);return {"id":enrollment.id,"student_id":student_id,"course_id":course_id,"status":enrollment.status.value}
    def course_progress(self,token:str,course_id:str)->dict[str,Any]:return asdict(self.learning.progress(self._student_id(token),course_id))
    def learning_path(self,token:str,course_id:str)->dict[str,Any]:
        snapshot=self.learning.learning_path_snapshot(self._student_id(token),course_id);data=asdict(snapshot)
        for step in data["steps"]:step["status"]=step["status"].value if hasattr(step["status"],"value") else step["status"]
        return data
    def next_lesson(self,token:str,course_id:str)->dict[str,Any]|None:
        lesson=self.learning.next_lesson(self._student_id(token),course_id);return asdict(lesson) if lesson else None
    def start_lesson(self,token:str,course_id:str,lesson_id:str)->dict[str,Any]:
        enrollment=self.learning.start_lesson(self._student_id(token),course_id,lesson_id);return {"course_id":course_id,"lesson_id":lesson_id,"status":enrollment.status.value}
    def complete_lesson(self,token:str,course_id:str,lesson_id:str)->dict[str,Any]:
        enrollment=self.learning.complete_lesson(self._student_id(token),course_id,lesson_id);return {"course_id":course_id,"lesson_id":lesson_id,"status":enrollment.status.value}
    def start_tutor_session(self,token:str,mode:str="text",lesson_id:str|None=None)->dict[str,Any]:return asdict(self.learning.start_tutor_session(self._student_id(token),mode=mode,lesson_id=lesson_id))

import io
import logging
from datetime import datetime, time, timezone
from aira_os.telegram.app import TelegramApplication
from aira_os.telegram.config import TelegramConfig
from aira_os.telegram.gateway import TelegramGateway
from aira_os.telegram.models import ActionProposal, MessageType
from aira_os.telegram.notifications import NotificationLevel, NotificationPolicy
from aira_os.telegram.security import RedactingFilter, Security
from aira_os.telegram.storage import Store


class Transport:
    def __init__(self): self.calls=[]
    def __call__(self, method, data):
        self.calls.append((method,data))
        if method == "getFile": return {"result":{"file_path":"voice/a.ogg"}}
        return {"ok":True}
    def download(self, remote, destination): destination.write_bytes(b"media")

class Core:
    def respond(self, message, session, context): return "Привет 💜 Я здесь. Что будем делать?"
    def status(self): return {"status":"OK","modules":["Memory","Guardian"]}
    def tasks(self): return [{"status":"RUNNING","title":"Research"}]
    def research(self, query, session): return "Хорошо. Начинаю анализ."
    def cancel(self, session): return True

class Perception:
    def understand(self,path,kind,caption): return f"understood {kind}: {caption}"
class Speech:
    def transcribe(self,path): return "голосовой текст"
    def synthesize(self,text): return "/tmp/voice.ogg"

def config(tmp_path):
    return TelegramConfig("secret-token","hook-secret",42,database_path=str(tmp_path/"test.db"),media_path=str(tmp_path/"media"))
def update(uid=1,user=42,text="Аира, привет"):
    return {"update_id":uid,"message":{"message_id":10,"chat":{"id":42},"from":{"id":user},"date":1,"text":text}}

def test_normalization_all_inputs(tmp_path):
    gateway=TelegramGateway(config(tmp_path),Transport())
    assert gateway.normalize(update()).type == MessageType.TEXT
    assert gateway.normalize(update(text="/start")).type == MessageType.COMMAND
    for key, kind in [("voice",MessageType.VOICE),("video",MessageType.VIDEO),("document",MessageType.DOCUMENT),("audio",MessageType.AUDIO)]:
        raw=update(); raw["message"].pop("text"); raw["message"][key]={"file_id":"x"}
        assert gateway.normalize(raw).type == kind
    raw=update(); raw["message"].pop("text"); raw["message"]["photo"]=[{"file_id":"small"},{"file_id":"large"}]
    assert gateway.normalize(raw).media_references[0]["file_id"] == "large"

def test_webhook_auth_queue_idempotency_and_text_e2e(tmp_path):
    transport=Transport(); cfg=config(tmp_path); app=TelegramApplication(cfg,Core(),gateway=TelegramGateway(cfg,transport))
    assert app.ingest("wrong",update())[0] == 401
    assert app.ingest("hook-secret",update()) == (202,{"ok":True,"queued":True})
    assert app.ingest("hook-secret",update()) == (202,{"ok":True,"queued":False})
    assert app.worker.run_once(); assert not app.worker.run_once()
    assert [x for x in transport.calls if x[0]=="sendMessage"][-1][1]["text"].startswith("Привет")
    assert len(app.store.history(app.store.session(42,42).session_id)) == 2

def test_founder_isolation(tmp_path):
    transport=Transport(); cfg=config(tmp_path); app=TelegramApplication(cfg,Core(),gateway=TelegramGateway(cfg,transport))
    app.ingest("hook-secret",update(user=99)); app.worker.run_once()
    assert "только владельцу" in transport.calls[-1][1]["text"]
    assert app.store.db.execute("select count(*) from sessions").fetchone()[0] == 0

def test_voice_photo_document_perception(tmp_path):
    transport=Transport(); cfg=config(tmp_path); app=TelegramApplication(cfg,Core(),Perception(),Speech(),gateway=TelegramGateway(cfg,transport))
    for i,key in enumerate(("voice","photo","document"),10):
        raw=update(i); raw["message"].pop("text"); raw["message"]["caption"]="inspect"
        raw["message"][key]=([{"file_id":"x","file_unique_id":str(i)}] if key=="photo" else {"file_id":"x","file_unique_id":str(i)})
        app.ingest("hook-secret",raw); app.worker.run_once()
    sent=[x[1]["text"] for x in transport.calls if x[0]=="sendMessage"]
    assert "голосовой текст" not in sent  # core, not Telegram, owns response intelligence
    assert len(sent) == 3

def test_commands_kill_switch_and_tasks(tmp_path):
    transport=Transport(); cfg=config(tmp_path); app=TelegramApplication(cfg,Core(),gateway=TelegramGateway(cfg,transport))
    for i,text in enumerate(("/start","/status","/tasks","/pause","/research topic","/resume","/research topic"),20):
        app.ingest("hook-secret",update(i,text=text)); app.worker.run_once()
    sent=[x[1]["text"] for x in transport.calls if x[0]=="sendMessage"]
    assert "Режим основателя" in sent[0] and "RUNNING" in sent[2]
    assert sent[4] == "Автономность приостановлена." and sent[6] == "Хорошо. Начинаю анализ."

def test_proposal_callback_exact_owner_and_once(tmp_path):
    transport=Transport(); cfg=config(tmp_path); store=Store(cfg.database_path); p=ActionProposal("publish","post ready",42); store.save_proposal(p)
    app=TelegramApplication(cfg,Core(),gateway=TelegramGateway(cfg,transport),store=store)
    callback=lambda uid,user:{"update_id":uid,"callback_query":{"id":str(uid),"from":{"id":user},"data":f"proposal:{p.proposal_id}:approve","message":{"message_id":3,"chat":{"id":42}}}}
    app.ingest("hook-secret",callback(30,99)); app.worker.run_once(); assert store.proposal(p.proposal_id)["status"] == "PENDING"
    app.ingest("hook-secret",callback(31,42)); app.worker.run_once(); assert store.proposal(p.proposal_id)["status"] == "APPROVED"
    app.ingest("hook-secret",callback(32,42)); app.worker.run_once(); assert "Уже обработано" in transport.calls[-1][1]["text"]

def test_session_history_is_bounded(tmp_path):
    store=Store(str(tmp_path/"db")); session=store.session(1,2)
    assert store.session(1,2).session_id == session.session_id
    for i in range(50): store.add_history(session.session_id,"user",str(i))
    assert len(store.history(session.session_id,100)) == 40

def test_security_and_token_redaction():
    security=Security(42,"secret")
    assert security.verify_webhook("secret") and not security.authorize(7)
    record=logging.LogRecord("x",logging.INFO,"",0,"token bot123:ABC-secret",(),None)
    RedactingFilter(["ABC-secret"]).filter(record)
    assert "ABC-secret" not in record.getMessage()

def test_wsgi_returns_quickly(tmp_path):
    app=TelegramApplication(config(tmp_path),Core())
    environment={"PATH_INFO":"/integrations/telegram/webhook","REQUEST_METHOD":"POST","CONTENT_LENGTH":"0","wsgi.input":io.BytesIO(b"")}
    statuses=[]; assert app.wsgi(environment,lambda status,headers: statuses.append(status)) == [b'{"ok":false}']
    assert statuses == ["400 Bad Request"]

def test_notification_policy_quiet_hours_and_deduplication():
    policy=NotificationPolicy(quiet_start=time(22),quiet_end=time(7))
    late=datetime(2026,1,1,23,tzinfo=timezone.utc)
    assert not policy.allows(NotificationLevel.INFO,"digest",late)
    assert policy.allows(NotificationLevel.CRITICAL,"security",late)
    assert not policy.allows(NotificationLevel.CRITICAL,"security",late)

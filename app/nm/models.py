from sqlalchemy import Column, String, JSON, DateTime, Integer
from database import Base, session
from datetime import datetime

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = ({'schema':'public'},)

    push_id = Column(String, nullable=False)
    message = Column(JSON, nullable=False)
    web_push_subscription = Column(JSON)
    created = Column(DateTime, default=datetime.utcnow)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    @classmethod
    def pop_messages(cls, push_id):
        obj = cls.query.filter(cls.push_id==push_id).order_by(cls.created).all()
        messages = [message.message for message in obj]

        for obj in obj:
            session.delete(obj)
        session.commit()
        session.close()

        return messages

    @classmethod
    def persist_message(cls, push_id, message, web_push_subscription=None):
        obj = cls(push_id=push_id, message=message, web_push_subscription=web_push_subscription)
        session.add(obj)
        session.commit()
        session.close()

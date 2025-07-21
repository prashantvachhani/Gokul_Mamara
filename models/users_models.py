from models import db
import uuid
from sqlalchemy.dialects.postgresql import UUID  


class Users(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)  
    name = db.Column(db.String(250), nullable=False )
    email = db.Column(db.String(250), unique=True, nullable=False)
    number = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=True, nullable=False)

    def User_data(self):
        return {
            'id' : self.id,
            'uuid': self.uuid,
            'name': self.name,
            'email': self.email,
            'number': self.number,
        }
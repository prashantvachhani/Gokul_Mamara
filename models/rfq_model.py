from models import db
from datetime import datetime, timezone

class RFQ_live(db.Model):  
    __tablename__ = 'live_rfq'
    rfq_id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category_name = db.Column(db.String(250), nullable=False)
    weight = db.Column(db.Float, nullable=False)  
    product_name = db.Column(db.String(250), nullable=False)

    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc))
    branch_name = db.Column(db.String(100), nullable=False)

    rfq_start_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    rfq_end_date = db.Column(db.DateTime)
    lifting_start_date = db.Column(db.DateTime)
    lifting_end_date = db.Column(db.DateTime)
    status = db.Column(db.String(255), nullable=False, default='upcoming')

    def RFQ_Data(self):
        return {
            "rfq_id": self.rfq_id,
            "qty": self.qty,
            "price": self.price,
            "category_name": self.category_name,
            "weight": self.weight,
            "product_name": self.product_name,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "branch_name": self.branch_name,
            "rfq_start_date": self.rfq_start_date.strftime('%Y-%m-%d %H:%M:%S') if self.rfq_start_date else None,
            "rfq_end_date": self.rfq_end_date.strftime('%Y-%m-%d %H:%M:%S') if self.rfq_end_date else None,
            "lifting_start_date": self.lifting_start_date.strftime('%Y-%m-%d %H:%M:%S') if self.lifting_start_date else None,
            "lifting_end_date": self.lifting_end_date.strftime('%Y-%m-%d %H:%M:%S') if self.lifting_end_date else None,
            "status": self.status
        }

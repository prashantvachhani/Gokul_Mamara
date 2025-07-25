from models import db
from datetime import time

class RFQ_PRICE(db.Model):
    __tablename__ = 'live_rfq_price'
    
    id = db.Column(db.Integer, primary_key=True)
    live_rfq_id = db.Column(db.Integer, db.ForeignKey('live_rfq.rfq_id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    supplier_name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    resion = db.Column(db.String(1000), nullable=True)
    date = db.Column(db.Integer, default=lambda: int(time.time()))


    def rfq_price_data(self):
        from datetime import datetime
        return {
            'id': self.id,
            'live_rfq_id': self.live_rfq_id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'qty': self.qty,
            'price': self.price,
            'status': self.status,
            'resion': self.resion,
            'date': datetime.fromtimestamp(self.date).strftime('%Y-%m-%d %H:%M:%S')
        }

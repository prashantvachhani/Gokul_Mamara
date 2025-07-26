from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime, timezone
from models import db
from confige import Config
from models.users_models import Users
from models.rfq_model import RFQ_live
from models.rfq_price_model import RFQ_PRICE

app = Flask(__name__)
app.config.from_object(Config)
app.config["JWT_SECRET_KEY"] = "pdqlocalhostljansddt"

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# ------------------ User Routes ------------------

@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():  
    data = request.get_json()
    new_user = Users(
        name=data['name'],
        email=data['email'],
        number=data['number'],
        password=data['password']
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.User_data()), 201

@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = Users.query.all()
    all_users_data = [user.User_data() for user in users]
    return jsonify({'users': all_users_data}), 200

@app.route('/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user_by_id(id):
    try:
        user = Users.query.get_or_404(id)
        return jsonify({'user': user.User_data()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    data = request.get_json()
    user = Users.query.get_or_404(id)

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.number = data.get('number', user.number)
    user.password = data.get('password', user.password)

    db.session.commit()
    return jsonify({'User_Updated': user.User_data()})

@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User with id {id} deleted successfully.'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Users.query.filter_by(email=data.get('email')).first()

    if not user or user.password != data.get('password'):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))  # identity as string to avoid "Subject must be a string"
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.User_data()
    })


# ------------------ RFQ Routes ------------------

# rfq data send Api
@app.route('/rfq', methods=['POST'])
@jwt_required()
def create_rfq():
    try:
        data = request.get_json()

        # Parse datetimes and make them timezone-aware (UTC)
        rfq_start = datetime.strptime(data['rfq_start_date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        rfq_end = datetime.strptime(data['rfq_end_date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        lifting_start = datetime.strptime(data['lifting_start_date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        lifting_end = datetime.strptime(data['lifting_end_date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)

        # Determine status based on current datetime and RFQ dates
        if now < rfq_start:
            dynamic_status = "upcoming"
        elif rfq_start <= now <= rfq_end:
            dynamic_status = "Live"
        else:
            dynamic_status = "closed"

        # Create new RFQ entry
        new_rfq = RFQ_live(
            qty=data['qty'],
            price=data['price'],
            category_name=data['category_name'],
            weight=data['weight'],
            product_name=data['product_name'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            branch_name=data['branch_name'],
            rfq_start_date=rfq_start,
            rfq_end_date=rfq_end,
            lifting_start_date=lifting_start,
            lifting_end_date=lifting_end,
            status=dynamic_status
        )
        db.session.add(new_rfq)
        db.session.commit()
        return jsonify({
            'message': 'RFQ added successfully.',
            'rfq': new_rfq.RFQ_Data()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# all rfq data fetching display route
@app.route('/rfq', methods=['GET'])
@jwt_required()
def get_rfq():
    rfqs = RFQ_live.query.all()
    return jsonify([rfq.RFQ_Data() for rfq in rfqs])

# single value fetch routing 
@app.route('/rfq/<int:id>', methods=['GET'])
@jwt_required()
def get_rfq_by_id(id):
    try:
        rfq = RFQ_live.query.get_or_404(id)
        return jsonify(rfq.RFQ_Data()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# rfq data update Api
@app.route('/rfq/<int:id>', methods=['PUT'])
@jwt_required()
def update_rfq(id):
    try:
        data = request.get_json()
        rfq = RFQ_live.query.get_or_404(id)

        rfq.qty = data.get('qty', rfq.qty)
        rfq.price = data.get('price', rfq.price)
        rfq.category_name = data.get('category_name', rfq.category_name)
        rfq.weight = data.get('weight', rfq.weight)
        rfq.product_name = data.get('product_name', rfq.product_name)
        rfq.date = datetime.strptime(data.get('date', rfq.date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        rfq.branch_name = data.get('branch_name', rfq.branch_name)
        rfq.rfq_start_date = datetime.strptime(data.get('rfq_start_date', rfq.rfq_start_date.strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        rfq.rfq_end_date = datetime.strptime(data.get('rfq_end_date', rfq.rfq_end_date.strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        rfq.lifting_start_date = datetime.strptime(data.get('lifting_start_date', rfq.lifting_start_date.strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        rfq.lifting_end_date = datetime.strptime(data.get('lifting_end_date', rfq.lifting_end_date.strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        rfq.status = data.get('status', rfq.status)

        db.session.commit()
        return jsonify({
            'message': 'RFQ updated successfully.',
            'rfq': rfq.RFQ_Data()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# rfq delete api
@app.route('/rfq/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_rfq(id):
    try:
        rfq = RFQ_live.query.get_or_404(id)
        db.session.delete(rfq)
        db.session.commit()
        return jsonify({
            'message': f'RFQ with ID {id} deleted successfully.'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# send-price Api
STATUS_MAP = {
    "Original": 0,
    "Confirmed": 1,
    "Rejected": 2,
    "Offered": 3
}

@app.route('/live-rfq-price', methods=['POST'])
@jwt_required()
def add_live_rfq_price():
    try:
        data = request.get_json()

        # Convert status string to integer if needed
        status = STATUS_MAP.get(data['status'], data['status'])

        # Get supplier from DB using supplier_id from JSON
        supplier = Users.query.get(data['supplier_id'])
        if not supplier:
            return jsonify({'error': 'Supplier not found'}), 404

        # Get RFQ from DB using live_rfq_id from JSON
        live_rfq = RFQ_live.query.get(data['live_rfq_id'])
        if not live_rfq:
            return jsonify({'error': 'RFQ not found'}), 404
        
        # Create new RFQ price entry
        new_data = RFQ_PRICE(
            live_rfq_id=live_rfq.rfq_id,
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            qty = data.get('qty') or live_rfq.qty,
            price = data.get('price') or live_rfq.price,
            status=status,
            resion=data.get('resion') if status == STATUS_MAP.get("Rejected") else None,
            date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
        )
        db.session.add(new_data)
        db.session.commit()
        return jsonify({
            'message': 'Live RFQ price added successfully.',
            'data': new_data.rfq_price_data()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

# Send price get api
@app.route('/live-rfq-price', methods=['GET'])
@jwt_required()
def get_send_price():
    try:
        data = RFQ_PRICE.query.all()
        return jsonify([priceee.rfq_price_data() for priceee in data])
    except Exception as error:
        return jsonify({'Error': str(error)})
    
# Price one value get api
@app.route('/live-rfq-price/<int:id>', methods=['GET'])
@jwt_required()
def get_one_price(id):
    try:
        data = RFQ_PRICE.query.get_or_404(id)
        return jsonify(data.rfq_price_data())
    except Exception as error:
        return jsonify({'Error': str(error)})

# ------------------ Run App ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)

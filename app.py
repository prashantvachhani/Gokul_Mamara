from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from models import db
from confige import Config
from models.users_models import Users
from models.rfq_model import RFQ_live

app = Flask(__name__)
app.config.from_object(Config)
app.config["JWT_SECRET_KEY"] = "lsouglopjmnvugf"

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# ------------------ User Routes ------------------

@app.route('/users', methods=['POST'])
def create_user():  # User creation shouldn't require a token
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

@app.route('/rfq', methods=['GET'])
@jwt_required()
def get_rfq():
    rfqs = RFQ_live.query.all()
    return jsonify([rfq.RFQ_Data() for rfq in rfqs])

@app.route('/rfq', methods=['POST'])
@jwt_required()
def create_rfq():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        new_rfq = RFQ_live(
            qty=data['qty'],
            price=data['price'],
            category_name=data['category_name'],
            weight=data['weight'],
            product_name=data['product_name'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            branch_name=data['branch_name'],
            rfq_start_date=datetime.strptime(data['rfq_start_date'], '%Y-%m-%d %H:%M:%S'),
            rfq_end_date=datetime.strptime(data['rfq_end_date'], '%Y-%m-%d %H:%M:%S'),
            lifting_start_date=datetime.strptime(data['lifting_start_date'], '%Y-%m-%d %H:%M:%S'),
            lifting_end_date=datetime.strptime(data['lifting_end_date'], '%Y-%m-%d %H:%M:%S')
        )
        db.session.add(new_rfq)
        db.session.commit()

        return jsonify({
            'message': 'RFQ added successfully.',
            'rfq': new_rfq.RFQ_Data()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ------------------ Run App ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=3000, debug=True)

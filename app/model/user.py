import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(db.Model):
    user_id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, default=True)
    create_time = db.Column(db.Date)

    def __init__(self, username, email, password, *args, **kwargs):
        super(db.Model, User).__init__(*args, **kwargs)
        self.user_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = "trial_user"
        self.create_time = datetime.now()

    def set_password(self, password):
        self.password = str(generate_password_hash(password))
        return self.password

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_role(self, role):
        from app.util.user_display import user_display
        if role in user_display:
            self.role = role
        return self.role

    @property
    def is_authenticated(self):
        if self.user_id:
            return True
        return False

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()


class UserPlan(db.Model):
    plan_id = db.Column(db.String(64), primary_key=True)
    plan_name = db.Column(db.String(128))
    plan_type = db.Column(db.String(32), index=True)
    plan_quota = db.Column(db.Integer)
    create_time = db.Column(db.Date)

    def __init__(self, plan_name, plan_type, plan_quota, *args, **kwargs):
        super(db.Model, UserPlan).__init__(*args, **kwargs)
        self.plan_id = str(uuid.uuid4())
        self.plan_name = plan_name
        self.plan_type = plan_type
        self.plan_quota = plan_quota
        self.create_time = datetime.now()


class PlanUsage(db.Model):
    usage_id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('user.user_id'))
    plan_id = db.Column(db.String(64), db.ForeignKey('user_plan.plan_id'))
    usage = db.Column(db.Integer)
    expiration = db.Column(db.Date)
    create_time = db.Column(db.Date)

    def __init__(self, user_id, plan_id):
        self.usage_id = str(uuid.uuid4())
        self.user_id = user_id
        self.plan_id = plan_id
        self.usage = 0
        self.create_time = datetime.now()

    def set_expiration(self, ex_time):
        self.expiration = ex_time

    def renewal(self):
        self.expiration = datetime.now() + timedelta(days=365)


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, \
    MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app import db, login
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from datetime import datetime


class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class Registration(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is already registered.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('This email is already registered.')


class UploadForm(FlaskForm):
    file = FileField('image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только картинки, пирожок!' )])
    submit = SubmitField('Загрузить')


class EditProfile(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone_number', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, orig_username, orig_email, orig_phone):
        super().__init__()
        self.orig_username = orig_username
        self.orig_email = orig_email
        self.orig_phone = orig_phone

    def validate_username(self, username):
        if username.data != self.orig_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('This username is already registered.')

    def validate_phone(self, phone):
        print(self.orig_phone)
        if phone.data != self.orig_phone:
            phone = User.query.filter_by(phone=phone.data).first()
            if phone is not None:
                raise ValidationError('This phone number is already registered.')

    def validate_email(self, email):
        if email.data != self.orig_email:
            email = User.query.filter_by(email=email.data).first()
            if email is not None:
                raise ValidationError('This email is already registered.')


class CreateAd(FlaskForm):
    name = StringField('Product name', validators=[DataRequired('Это поле должно быть заполнено'), Length(min=5, max=20)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=120)])
    price = IntegerField('Price', validators=[DataRequired()])
    image = MultipleFileField('image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images Only')])
    submit = SubmitField('Create')


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

########################################## базы данных ################################################


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    phone = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    products = db.relationship('Product', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(32))
    product_description = db.Column(db.String(300))
    product_price = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_images = db.relationship('ProductImage', cascade='all,delete', backref='image', lazy='dynamic')


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(120))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))




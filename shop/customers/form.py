from wtforms import StringField,Form,TextAreaField,PasswordField,SubmitField,validators
from flask_wtf.file import file_required,file_allowed,FileField

class CustomerRegisterForm():
    name = StringField('Name:')
    username = StringField('Username:',[validators.DataRequired()])
    email = StringField('Email:', [validators.Email(),validators.DataRequired()])
    password = PasswordField('Password:',[validators.DataRequired,validators.EqualTo('confirm',
    message='Both password must match!')])
    confirm = PasswordField('Repeat password:',[validators.DataRequired()])
    country = StringField('Country:',[validators.DataRequired()])
    state = StringField('State:',[validators.DataRequired()])
    city = StringField('City:',[validators.DataRequired()])
    contact = StringField('contact:',[validators.DataRequired()])
    address = StringField('Address :',[validators.DataRequired()])
    zip_code = StringField('Zip code:',[validators.DataRequired()])
    profile = FileField('Profile',validators=[file_allowed(['jpg','png','gif','jpeg'],'Image only please')])
    submit = SubmitField('Register')

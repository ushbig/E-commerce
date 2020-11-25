from flask import Flask,render_template,session,redirect,url_for,flash,request,current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import column,String,Integer,ForeignKey,table,DateTime
from datetime  import datetime
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES,UploadSet,configure_uploads,patch_request_class
from flask_msearch import Search
from flask_login import login_manager,login_required,current_user,logout_user,login_user,UserMixin,LoginManager
import os
import secrets
from jinja2 import Template
import json


from wtforms import StringField,Form,TextAreaField,PasswordField,SubmitField,validators,ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired,FileAllowed,FileField,file_required
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = '\xaeb\x87\xb0|\xb0\xbf+\tn\x8dH\xea3\xa7t/\x1d\xdfT\x19\x1b7\xea'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myshop.db'
app.config['UPLOADED_PHOTOS_DEST']=os.path.join(basedir, 'static/image')

photos = UploadSet('photos',IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


db =SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)
migrate = Migrate(app,db)
with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app,db,render_as_batch=True)
    else:
        migrate.init_app(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_veiw = 'customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = u'Please Login first'


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    
    name =db.Column(db.String(30), nullable=False, unique=True)
    username =db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password=db.Column(db.String(120),unique=False, nullable=False) 
    photo  = db.Column(db.String(120),unique=False ,nullable=True) 
    

    def __repr__(self):
        return 'User' +  self.name

class CustomerRegisterForm(FlaskForm):
    name = StringField('Name:')
    username = StringField('Username:',[validators.DataRequired()])
    email = StringField('Email:',[validators.Email(),validators.DataRequired()])
    password = PasswordField('Password:',[validators.DataRequired(),validators.EqualTo
    ('confirm',message='Both password must match!')])
    confirm = PasswordField('Repeat password:',[validators.DataRequired()])
    country = StringField('Country:',[validators.DataRequired()])
    #state = StringField('State:',[validators.DataRequired()])
    city = StringField('City:',[validators.DataRequired()])
    contact = StringField('contact:',[validators.DataRequired()])
    address = StringField('Address :',[validators.DataRequired()])
    zipcode = StringField('Zip code:',[validators.DataRequired()])
    profile = FileField('Profile',validators=[FileAllowed(['jpg','jpeg','png','gif'],'Image only please')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError('Username is already in use!')
    
    def validate_email(self, email):
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError('email address is already in use!')

class CustomerLoginForm(FlaskForm):

    email = StringField('Email:',[validators.Email(),validators.DataRequired()])
    password = PasswordField('Password:',[validators.DataRequired()])


@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)

class jsonEcodedDict(db.TypeDecorator):
    impl = db.Text
    def set_value(self,value,dialect):
        if value is None :
            return '{}'
        else:
            json.dumps(value)

    def get_value(self,value,dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)
            
class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20),unique=True,nullable=False)
    status = db.Column(db.String(20),default='pending',nullable=False)
    customer_id = db.Column(db.Integer,unique=False,nullable=False)
    date_created = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    orders = db.Column(jsonEcodedDict)

    def __repr__(self):
        return '<CustomerOrder %r>' % self.invoice

class Register(db.Model,UserMixin):
    __tablename__ = "Register"
    id = db.Column(db.Integer, primary_key=True)
    
    name =db.Column(db.String(30),unique=False)
    username = db.Column(db.String(30),unique=True )
    email = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(200), unique=False)
    country = db.Column(db.String(50),  unique=False)
    #state = db.Column(db.String(50),  unique=False)
    city = db.Column(db.String(50),  unique=False)
    contact = db.Column(db.String(50),  unique=False)
    address = db.Column(db.String(50),  unique=False)
    zipcode = db.Column(db.String(50),  unique=False)
    profile =db.Column(db.String(200),  unique=False ,default='profile.jpg')
    date_craeted = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.name



class Addproduct(db.Model):

    __tablename__ = "Addproduct"
    __seachable__ = ['name', 'desc']
    
    id = db.Column(db.Integer, primary_key=True)
    
    name =db.Column(db.String(30), nullable=False, unique=True)
    price = db.Column(db.Numeric(10,2),  nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    colors = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    image_1 = db.Column(db.String(150),nullable=False)
    image_2 = db.Column(db.String(150),nullable=False)
    image_3 = db.Column(db.String(150),nullable=False)

    brand_id = db.Column(db.Integer,db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('brands', lazy=True))


    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))
    

    def __repr__(self):
        return 'Addproduct' +  self.name



class Brand(db.Model):
    __tablename__ = "brand"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30), nullable=False,unique=True)
class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30),nullable=False,unique=True)
db.create_all()

    
def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1 ,dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))

    return False



@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        colors = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and colors and request.method=='POST':
            DictItems = {product_id:{'name':product.name, 'price':product.price,'discount':product.discount,'color':colors,'quantity':quantity,'image':product.image_1}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    print('Product is already in your cart')
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e :
        print(e)
    finally:
        return redirect(request.referrer)

   


@app.route('/customers/register',methods=['GET','POST'])
def Customer_registration():
    form = CustomerRegisterForm()
    
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data,username=form.username.data,email =form.email.data,
        password=hash_password,country=form.country.data,state=form.state.data,contact=form.contact.data,city=form.city.data,address=form.address.data,zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.username.data} Thank you for registering','success')
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('customers/register.html',form=form,title='Customer Registration Page')

@app.route('/customers/login', methods=['GET','POST'])
def customerLogin():
    form= CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            flash('You are login now!','success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect password or email','danger')
        return redirect(url_for('customerLogin'))
    return render_template('customers/login.html',form=form)
@app.route('/customers/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('customerLogin'))

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated :
        current_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            pass
        except Exception as e:
            print(e)
            flash('Some thing went wrong while getting order','danger')
            

@app.route('/')
def home():
    page =request.args.get('page',1,type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0 ).order_by(Addproduct.id.desc()).paginate(page=page,per_page=8)
    barnds =  Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
 
    return render_template('products/index.html', products = products, barnds=barnds,categories=categories) 




@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name', 'desc'], limit=3)
    return render_template('products/result.html', products=products)




@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    barnds =  Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return render_template('/products/single_page.html',product=product,barnds=barnds,categories=categories)


@app.route('/brand/<int:id>')
def get_brand(id):
    get_b = Brand.query.filter_by(id=id).first_or_404()
    page = request.args.get('page',1,type=int)
    brand = Addproduct.query.filter_by(brand=get_b).paginate(page=page,per_page=6)
    barnds =  Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return render_template('products/index.html',brand=brand,barnds=barnds,categories=categories,get_b=get_b)

@app.route('/categories/<int:id>')
def get_category(id):
    page =request.args.get('page',1,type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page,per_page=6)
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    barnds =  Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    return render_template('products/index.html', get_cat_prod=get_cat_prod,categories=categories,barnds=barnds,get_cat=get_cat)

@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))
   
    return render_template('products/index.html', title=' Admin Page')

@app.route('/register' , methods=['GET', 'POST'])
def register():

    

    if request.method == 'POST':
        hash_password = bcrypt.generate_password_hash(request.form['password'])
      
        
        confirm=request.form['confirm']
            
        user = User(name=request.form['name'],username=request.form['username'],email=request.form['email'],password=hash_password)

        db.session.add(user)
        db.session.commit()
        flash(f"Thank you for subscribing...",'success')
        return redirect(url_for('home'))
            
    return render_template('register.html'  , title ="Registeration page" )


@app.route('/login', methods=['GET','POST'])
def login():

    

    if request.method =='POST':
        user = User.query.filter_by(email= request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            session['email'] = request.form['email']
            flash(f'Welcome, you are logged in','success')
            return redirect(request.args.get('next') or url_for('login'))

        else:
            flash(f'Wrong password try  again', 'danger')
         
    



    return render_template('login.html', title ="Login page" )

@app.route('/brands')
def brand():
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))

    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('brand.html', title='Brand Page',brands=brands)

@app.route('/category')
def category():
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))

    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('brand.html', title='Category Page',categories=categories)


@app.route('/updatebrand/<int:id>', methods=['GET','POST'])
def updatebrand(id):
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))
    
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')

    if request.method == 'POST':
        updatebrand.name = brand
        flash(f'Your brand has been updated','success')
        db.session.commit()
        return redirect(url_for('brand'))
    return render_template('updatebrand.html', title='Update Brand Page',updatebrand=updatebrand)


@app.route('/updatecat/<int:id>', methods=['GET','POST'])
def updatecat(id):
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))
    
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    

    if request.method == 'POST':
        updatecategory.name = category
        flash(f'Your category has been updated','success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('updatebrand.html', title='Update Category Page',updatecategory=updatecategory)
@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))

    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    
    if request.files.get('image_1'):
        try:
            os.unlink(os.path.join(current_app.root_path,'static/image' + product.image_1))
            product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        except:
            product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')

    if request.files.get('image_2'):
        try:
            os.unlink(os.path.join(current_app.root_path,'static/image' + product.image_2))
            product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
        except:
            product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')

    if request.files.get('image_3'):
        try:
            os.unlink(os.path.join(current_app.root_path,'static/image' + product.image_3))
            product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
        except:
            product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')

    db.session.commit()
    
    
    return render_template('updateproduct.html', title='Update Category Page',brands=brands,categories=categories,product=product)

@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))

    brand = Brand.query.get_or_404(id)
    if request.method ==  'POST':
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand{brand.name} was deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f'The brand{brand.name} cant be deleted ', 'success')
    return redirect(url_for('index'))

@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))

    product = Addproduct.query.get_or_404(id)
    if request.method ==  'POST':
       
        try:
            os.unlink(os.path.join(current_app.root_path,'static/image' + product.image_1))
            os.unlink(os.path.join(current_app.root_path,'static/image' + product.image_2))
            os.unlink(os.path.join(current_app.root_path,'static/image' + product.image_3))
        except Exception as e:
            print(e)


        db.session.delete(product)
        db.session.commit()
        flash(f'The product{product.name} was deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f'The product{product.name} cant be deleted ', 'success')
    return redirect(url_for('index'))

@app.route('/deletecat/<int:id>', methods=['POST'])
def deletecat(id):
    if 'email' not in session:
        flash(f'Login in first','danger')
        return redirect(url_for('login'))

    category = Category.query.get_or_404(id)
    if request.method ==  'POST':
        db.session.delete(category)
        db.session.commit()
        flash(f'The category{category.name} was deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f'The brand{category.name} cant be deleted ', 'success')
    return redirect(url_for('index'))

@app.route('/addbrand',methods=['GET','POST'])
def addbrand():

    if 'email' not in session:
        flash(f'Please login First','danger')
        return redirect(url_for('login'))

    if request.method=='POST':
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        db.session.commit()
        flash(f'The Brand {getbrand } was added to your database','success')
        return redirect(url_for('brand'))
    return render_template('addbrand.html',brands='brands')

@app.route('/addcat',methods=['GET','POST'])
def addcat():
    if 'email' not in session:
        flash(f'Please login First','danger')
        return redirect(url_for('login'))


    if request.method=='POST':
        getbrand = request.form.get('category')
        cat = Category(name=getbrand)
        db.session.add(cat)
        db.session.commit()
        flash(f'The Category {getbrand } was added to your database','success')
        return redirect(url_for('addcat'))
    return render_template('addbrand.html')

@app.route('/addproduct', methods=['POST','GET'])
def addProduct():
    if 'email' not in session:
        flash(f'Please login First','danger')
        return redirect(url_for('login'))


    brands = Brand.query.all()
    categories = Category.query.all()

    if request.method=="POST":
        name = request.form['name']
        price = request.form['price']
        discount = request.form['discount']
        stock = request.form['stock']
        colors = request.form['colors']
        desc = request.form['desc']
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1=photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        image_2=photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.') 
        image_3=photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
        addpro = Addproduct(name=name,price=price,discount=discount,stock=stock,colors=colors,desc=desc,brand_id=brand,category_id=category,image_1=image_1,image_2=image_2,image_3=image_3)
        db.session.add(addpro)
        db.session.commit()
        flash(f'The product {name } was added to your database','success')
        return redirect(url_for('home'))



    return render_template('addProduct.html',brands=brands,categories=categories ,title='Add product page')

if __name__ == '__main__':
    app.run(debug=True)
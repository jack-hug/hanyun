import os
import shutil
import uuid
from datetime import datetime

import click
from faker import Faker
from flask import Flask, render_template, redirect, url_for, current_app, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.file import FileField, FileAllowed

from config import config
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from flask_moment import Moment
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user

app = Flask(__name__)

app.config.from_object(config['production'])

db = SQLAlchemy(app)
fake = Faker()
csrf = CSRFProtect(app)
ckeditor = CKEditor(app)
moment = Moment(app)
mail = Mail(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


def random_filename(filename):  # 图片随机命名
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def save_uploaded_files(request_files, product):  # 封装上传图片函数
    photos = []
    for f in request_files.getlist('photos'):
        if f.content_length > current_app.config['MAX_CONTENT_LENGTH']:
            flash(f'文件 {f.filename} 过大，上传的文件大小不能超过3MB')
            continue
        filename = random_filename(f.filename)
        f.save(os.path.join(current_app.config['HY_UPLOAD_PATH'], filename))
        photo = Photo(
            filename=filename,
            product=product
        )
        photos.append(photo)
    return photos


class Product(db.Model):  # 产品表
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    price = db.Column(db.Float)
    material = db.Column(db.String(200))
    level = db.Column(db.String(200))
    oem = db.Column(db.String(200))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    clicks = db.Column(db.Integer)


class Photo(db.Model):  # 图片表
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref=db.backref('photos', lazy='dynamic', cascade='all, delete-orphan'))
    source = db.Column(db.String(200), default='form')  # 区别图片来源


class About(db.Model):  # 关于我们表
    __tablename__ = 'about'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class Advantage(db.Model):  # 优势表
    __tablename__ = 'advantage'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class EditProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    price = StringField('Price', validators=[DataRequired(), Length(1, 20)])
    material = StringField('Material', validators=[Length(0, 200)])
    level = StringField('Level', validators=[Length(0, 200)])
    oem = StringField('OEM/ODM', validators=[Length(0, 200)])
    content = CKEditorField('Content')
    photos = FileField('Product Photo:', validators=[FileAllowed(['jpg', 'png', 'gif'], '只能上传图片')])
    submit = SubmitField('Submit')


class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    price = StringField('Price', validators=[DataRequired(), Length(1, 20)])
    material = StringField('Material', validators=[Length(0, 200)])
    level = StringField('Level', validators=[Length(0, 200)])
    oem = StringField('OEM/ODM', validators=[Length(0, 200)])
    content = CKEditorField('Content')
    photos = FileField('Product Photo:', validators=[FileAllowed(['jpg', 'png', 'gif'], '只能上传图片')])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


@app.context_processor
def make_template_context():
    return dict(
        products=Product.query.order_by(Product.id.asc()).all(),
        about=About.query.order_by(About.timestamp.desc()).first(),
        advantages=Advantage.query.order_by(Advantage.id.asc()).all()
    )


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    products = Product.query.order_by(Product.id.asc()).limit(8).all()
    return render_template('index.html', products=products)


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/company')
def company():
    return render_template('company.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get(product_id)
    recommends_products = Product.query.filter(Product.id != product_id).all()
    return render_template('product.html', product=product, recommends_products=recommends_products)


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])  # 编辑产品
def edit_product(product_id):
    form = EditProductForm()
    product = Product.query.get_or_404(product_id)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.material = form.material.data
        product.level = form.level.data
        product.oem = form.oem.data
        product.content = form.content.data
        product.timestamp = datetime.now()
        db.session.commit()

        if 'photos' in request.files and request.files['photos'].filename != '':
            photos = save_uploaded_files(request.files, product)
            db.session.add_all(photos)
            db.session.commit()
        flash('修改成功.', 'success')
        return redirect(url_for('admin'))

    form.name.data = product.name
    form.price.data = product.price
    form.material.data = product.material
    form.level.data = product.level
    form.oem.data = product.oem
    form.content.data = product.content
    return render_template('edit_product.html', form=form, product=product)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail(message='File type not allowed!')
    filename = random_filename(f.filename)
    f.save(os.path.join(current_app.config['HY_UPLOAD_PATH'], filename))
    url = url_for('get_image', filename=filename)

    return upload_success(url=url)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            product = Product(
                name=form.name.data,
                price=form.price.data,
                material=form.material.data,
                level=form.level.data,
                oem=form.oem.data,
                content=form.content.data,
                clicks=0,
                timestamp=datetime.now()
            )
            db.session.add(product)
            db.session.commit()

            if 'photos' in request.files and request.files['photos'].filename != '':
                photos = save_uploaded_files(request.files, product)
                db.session.add_all(photos)
                db.session.commit()
            flash('添加成功.', 'success')
            return redirect(url_for('admin'))

    return render_template('add_product.html', form=form)


@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('删除成功.', 'success')
    return redirect(url_for('admin'))


@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    db.session.delete(photo)
    db.session.commit()
    flash('图片删除成功.', 'success')
    return redirect(url_for('edit_product', product_id=photo.product_id))


@app.route('/uploads/<path:filename>')  # 获得上传图片
def get_image(filename):
    return send_from_directory(current_app.config['HY_UPLOAD_PATH'], filename)

# @app.route('/previous/<int:product_id>', methods=['GET', 'POST'])
# def previous_product(product_id):
#     product_id = Product.query.get_or_404(product_id)
#     if product_id.id == 1:
#         flash('已经是第一页了', 'warning')
#         return redirect(url_for('product', product_id=product_id.id))
#     else:
#         return redirect(url_for('product', product_id=product_id.id-1))
#
# @app.route('/next/<int:product_id>', methods=['GET', 'POST'])
# def next_product(product_id):
#     product_id = Product.query.get_or_404(product_id)
#     if product_id.id == len(Product.query.all()):
#         flash('已经是最后一页了', 'warning')
#         return redirect(url_for('product', product_id=product_id.id))
#     else:
#         return redirect(url_for('product', product_id=product_id.id+1))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data
        admin = Admin.query.first()
        if username == admin.username and admin.validate_password(password):
            login_user(admin, remember)
            flash('Welcome back.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('用户名或密码错误.', 'warning')
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run()


@app.cli.command()  # 生成数据
def forge():
    from fakes import fake_products, fake_about, fake_advantage
    click.echo('Drop tables....')
    db.drop_all()
    click.echo('Delete uploads photo...')
    if os.path.exists(current_app.config['HY_UPLOAD_PATH']):
        shutil.rmtree(current_app.config['HY_UPLOAD_PATH'])
        os.mkdir(current_app.config['HY_UPLOAD_PATH'])
    click.echo('Initialized database......')
    db.create_all()
    click.echo('Generating products...')
    fake_products()
    click.echo('Generating about_us text...')
    fake_about()
    click.echo('Generating advantage text...')
    fake_advantage()

    click.echo('Done.')

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create admin."""

    click.echo('Initializing the database...')
    db.create_all()
    admin = Admin.query.first()
    if admin:
        click.echo('The administrator already exists, updating...')
        admin.username = username
        admin.set_password(password)
    else:
        click.echo('Creating the temporary administrator account...')
        admin = Admin(
            username=username,
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        click.echo('Done.')


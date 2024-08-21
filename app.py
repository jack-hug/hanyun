import os
import random
import uuid
from datetime import datetime

import click
from faker import Faker
from faker.providers import DynamicProvider
from flask import Flask, render_template, redirect, url_for, current_app, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.file import FileField, FileAllowed

from config import config
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField

app = Flask(__name__)

app.config.from_object(config['development'])

db = SQLAlchemy(app)
fake = Faker()
csrf = CSRFProtect(app)
ckeditor = CKEditor(app)


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


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    price = db.Column(db.Float)
    description = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    clicks = db.Column(db.Integer)


class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref=db.backref('photos', lazy='dynamic', cascade='all, delete-orphan'))


class About(db.Model):
    __tablename__ = 'about'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)


class EditProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    price = StringField('Price', validators=[DataRequired(), Length(1, 20)])
    description = CKEditorField('Description', validators=[DataRequired(), Length(1, 100)])
    photos = FileField('Product Photo:', validators=[FileAllowed(['jpg', 'png', 'gif'], '只能上传图片')])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    price = StringField('Price', validators=[DataRequired(), Length(1, 20)])
    description = StringField('Description', validators=[DataRequired(), Length(1, 100)])
    photos = FileField('Product Photo:', validators=[FileAllowed(['jpg', 'png', 'gif'], '只能上传图片')])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


@app.context_processor
def make_template_context():
    return dict(
        products=Product.query.order_by(Product.id.asc()).all(),
        about=About.query.order_by(About.timestamp.desc()).first(),
    )


@app.route('/')
def index():
    return render_template('index.html')


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
    return render_template('product.html', product=product)


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/edit_products/<int:product_id>', methods=['GET', 'POST'])  # 编辑产品
def edit_products(product_id):
    form = EditProductForm()
    product = Product.query.get(product_id)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
        db.session.commit()
        print('aaa')
        if 'photos' in request.files and request.files['photos'].filename != '':
            photos = save_uploaded_files(request.files, product)
            db.session.add_all(photos)
            db.session.commit()
        flash('添加成功.', 'success')
        return redirect(url_for('admin'))
    elif form.cancel.data:
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.description.data = product.description
    return render_template('edit_products.html', form=form, product=product)


@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('edit_products'))


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
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
        return redirect(url_for('edit_products'))
    elif form.cancel.data:
        return redirect(url_for('admin'))
    return render_template('add_product.html', form=form)


@app.route('/uploads/<path:filename>')  # 获得上传图片
def get_image(filename):
    return send_from_directory(current_app.config['HY_UPLOAD_PATH'], filename)


if __name__ == '__main__':
    app.run()


@app.cli.command()
def initdb():
    db.create_all()
    print('Initialized the database.')


@app.cli.command()
@click.option('--product', default=8, help='Quantity of products, default is 8.')
def forge(product):
    click.echo('Drop tables....')
    db.drop_all()
    click.echo('Initialized database......')
    db.create_all()
    click.echo('Generating %d products...' % product)
    fake_products(product)
    click.echo('Generating about_us text...')
    fake_about()


fake_products = DynamicProvider(
    provider_name='products',
    elements=[
        'KPHF',
        'SCZN',
        'KOCUF',
        'SCZA',
        'MTGL',
        'KOCUS',
        'SCZNP',
        'BNPL'
    ],  # 8 products
)

fake.add_provider(fake_products)


def fake_products(count=8):
    unique_product = set()
    for i in range(count):
        while True:
            product_name = fake.products()
            if product_name not in unique_product:
                unique_product.add(product_name)
                click.echo('Generated unique product name: %s' % product_name)
                break

        product = Product(
            name=product_name,
            price=fake.random_int(min=0, max=100),
            description=fake.text(100),
            clicks=random.randint(1, 5000),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(product)
    db.session.commit()


def fake_about():
    about_us = '''HANYUN MOLD was founded in 2010, is a factory specializing in the production of standard slide core unit, precision positioning, various types of sliders, non-standard slide core units. The company is located in Dongguan and continues to develop with its superior geographical location. With more than 10 years of experience in tilting top slides, we have mastered every production step and know how to produce high-quality slides at low cost.

In order to shorten the delivery time, we always keep a large amount of semi-inventory and finished products all year round. After receiving the order, we can quickly deliver the products to our customer.

Because we have provided customers with advantageous prices and high-quality slides for many years, we have won the support and trust of our customers.
'''
    about = About(
        name='About Us',
        content=about_us,
        timestamp=fake.date_time_this_year()
    )
    db.session.add(about)
    db.session.commit()

import os
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
    description = db.Column(db.String(200))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    clicks = db.Column(db.Integer)


class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref=db.backref('photos', lazy='dynamic', cascade='all, delete-orphan'))
    source = db.Column(db.String(200), default='form')  # 区别图片来源


class About(db.Model):
    __tablename__ = 'about'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)


class Advantage(db.Model):
    __tablename__ = 'advantage'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)


class EditProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    price = StringField('Price', validators=[DataRequired(), Length(1, 20)])
    description = StringField('Description', validators=[DataRequired()])
    content = CKEditorField('Content')
    photos = FileField('Product Photo:', validators=[FileAllowed(['jpg', 'png', 'gif'], '只能上传图片')])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    price = StringField('Price', validators=[DataRequired(), Length(1, 20)])
    description = StringField('Description', validators=[DataRequired(), Length(1, 100)])
    content = CKEditorField('Content')
    photos = FileField('Product Photo:', validators=[FileAllowed(['jpg', 'png', 'gif'], '只能上传图片')])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


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


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])  # 编辑产品
def edit_product(product_id):
    form = EditProductForm()
    product = Product.query.get_or_404(product_id)
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect(url_for('admin'))
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
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
    form.description.data = product.description
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
    print('aaa2')
    form = AddProductForm()
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect(url_for('admin'))
        print('bbb')
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            content=form.content.data,
            clicks=0,
            timestamp=datetime.now()
        )
        print(product)
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


@app.route('/uploads/<path:filename>')  # 获得上传图片
def get_image(filename):
    return send_from_directory(current_app.config['HY_UPLOAD_PATH'], filename)


if __name__ == '__main__':
    app.run()


@app.cli.command()
@click.option('--product', default=8, help='Quantity of products, default is 8.')
def forge(product):
    from fakes import fake_products, fake_about, fake_advantage
    click.echo('Drop tables....')
    db.drop_all()
    click.echo('Initialized database......')
    db.create_all()
    click.echo('Generating %d products...' % product)
    fake_products(product)
    click.echo('Generating about_us text...')
    fake_about()
    click.echo('Generating advantage text...')
    fake_advantage()

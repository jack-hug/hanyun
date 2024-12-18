import os
import shutil
import uuid
from datetime import datetime

import click
from faker import Faker
from flask import Flask, render_template, redirect, url_for, current_app, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from config import config
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from flask_moment import Moment
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5

from emails import send_new_message_email

from dotenv import load_dotenv

load_dotenv('.flaskenv')

app = Flask(__name__)

app.config.from_object(config['production'])

db = SQLAlchemy(app)
fake = Faker()
csrf = CSRFProtect(app)
ckeditor = CKEditor(app)
moment = Moment(app)
mail = Mail(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap5(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'info'


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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.Column(db.Integer)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))


class Photo(db.Model):  # 图片表
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref=db.backref('photos', lazy='dynamic', cascade='all, delete-orphan'))
    source = db.Column(db.String(200), default='form')  # 区别图片来源


class About(db.Model):  # 关于我们表
    __tablename__ = 'about'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Advantage(db.Model):  # 优势表
    __tablename__ = 'advantage'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):  # 留言表
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    content = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class WebsiteInfo(db.Model):  # 网站信息表
    __tablename__ = 'website_info'
    id = db.Column(db.Integer, primary_key=True)
    quick_information = db.Column(db.Text(),
                                  default='Hanyun mold have more than 10 years of experience<br> in making slide core units.')
    company_name = db.Column(db.String(100), default='Shenzhen Hanyun Mold Co.,Ltd')
    company_address = db.Column(db.String(100))
    company_phone = db.Column(db.String(100))
    company_email = db.Column(db.String(100), default='karen@hanyunmold.com')

    skype = db.Column(db.String(100))
    facebook = db.Column(db.String(100))
    twitter = db.Column(db.String(100))
    line = db.Column(db.String(100))


class Admin(db.Model, UserMixin):  # 管理员表
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text())

    products = db.relationship('Product', backref='category')


class EditProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    category = SelectField('Category', coerce=int)
    price = StringField('Price', validators=[DataRequired(), Length(1, 20)])
    material = StringField('Material', validators=[Length(0, 200)])
    level = StringField('Level', validators=[Length(0, 200)])
    oem = StringField('OEM/ODM', validators=[Length(0, 200)])
    content = CKEditorField('Content')
    photos = FileField('Product Photo:', validators=[FileAllowed(['jpg', 'png', 'gif'], '只能上传图片')])
    submit = SubmitField('Submit')


class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    category = SelectField('Category', coerce=int)
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


class WebsiteInfoForm(FlaskForm):
    quick_information = TextAreaField('Quick Information', validators=[Length(0, 200)])
    company_name = StringField('Company Name', validators=[Length(0, 100)])
    company_address = StringField('Company Address', validators=[Length(0, 100)])
    company_phone = StringField('Company Phone', validators=[Length(0, 100)])
    company_email = StringField('Company Email', validators=[Length(0, 100)])
    skype = StringField('Skype', validators=[Length(0, 100)])
    facebook = StringField('Facebook', validators=[Length(0, 100)])
    twitter = StringField('Twitter', validators=[Length(0, 100)])
    line = StringField('Line', validators=[Length(0, 100)])
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 50)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(1, 800)])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(1, 128)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(1, 128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(1, 128),
                                                                     EqualTo('new_password',
                                                                             message='两次输入密码不一致!')])
    submit = SubmitField('Submit')

    def validate_new_password(self, new_password):
        if self.current_password.data == new_password.data:
            raise ValidationError('新密码不能和旧密码相同.')


class AddCategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[DataRequired(), Length(1, 50)])
    description = TextAreaField('分类简介', validators=[Length(0, 500)])
    submit = SubmitField('Submit')


class EditCategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[DataRequired(), Length(1, 50)])
    description = TextAreaField('分类简介', validators=[Length(0, 500)])
    submit = SubmitField('Submit')


@app.context_processor
def make_template_context():
    return dict(
        products=Product.query.order_by(Product.id.asc()).all(),
        about=About.query.order_by(About.timestamp.desc()).first(),
        advantages=Advantage.query.order_by(Advantage.id.asc()).all(),
        websiteinfo=WebsiteInfo.query.order_by(WebsiteInfo.id.desc()).first(),
        messages=Message.query.order_by(Message.timestamp.desc()).all(),
        messageform=MessageForm(),
        categories=Category.query.order_by(Category.id.asc()).all(),
    )


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET', 'POST'])
def index():
    products = Product.query.order_by(Product.id.asc()).limit(8).all()
    messageform = MessageForm()
    if messageform.validate_on_submit():
        message = Message(name=messageform.name.data, email=messageform.email.data, content=messageform.content.data)
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!We will reply to you as soon as possible!', 'success')

        send_new_message_email(messageform.email.data, messageform.content.data)
        messageform.name.data = ''
        messageform.email.data = ''
        messageform.content.data = ''
    return render_template('index.html', products=products, messageform=messageform)


@app.route('/category/<int:category_id>', methods=['GET', 'POST'])
def category(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('products.html', products=products, category_id=category_id, category=category)

@app.route('/company')  # 公司介绍
def company():
    return render_template('company.html')


@app.route('/contact', methods=['GET', 'POST'])  # 联系我们
def contact():
    messageform = MessageForm()
    if messageform.validate_on_submit():
        message = Message(name=messageform.name.data, email=messageform.email.data, content=messageform.content.data)
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!We will reply to you as soon as possible!', 'success')

        send_new_message_email(messageform.email.data, messageform.content.data)
        messageform.name.data = ''
        messageform.email.data = ''
        messageform.content.data = ''
    return render_template('contact.html', messageform=messageform)


@app.route('/product/<int:product_id>')  # 产品详情
def product(product_id):
    product = Product.query.get(product_id)
    recommends_products = Product.query.filter(Product.id != product_id).all()
    return render_template('product.html', product=product, recommends_products=recommends_products)


@app.route('/admin/products', methods=['GET', 'POST'])  # 后台
@login_required
def admin():
    products_length = Product.query.count()
    return render_template('admin.html', products_length=products_length)


@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])  # 编辑产品
@login_required
def edit_product(product_id):
    form = EditProductForm()
    product = Product.query.get_or_404(product_id)

    categories = Category.query.all()
    form.category.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():
        product.name = form.name.data
        product.category_id = form.category.data
        product.price = form.price.data
        product.material = form.material.data
        product.level = form.level.data
        product.oem = form.oem.data
        product.content = form.content.data
        product.timestamp = datetime.utcnow()
        db.session.commit()

        if 'photos' in request.files and request.files['photos'].filename != '':
            photos = save_uploaded_files(request.files, product)
            db.session.add_all(photos)
            db.session.commit()
        flash('修改成功.', 'success')
        return redirect(url_for('admin'))

    form.name.data = product.name
    form.category.data = product.category_id
    form.price.data = product.price
    form.material.data = product.material
    form.level.data = product.level
    form.oem.data = product.oem
    form.content.data = product.content
    return render_template('edit_product.html', form=form, product=product)


@app.route('/upload', methods=['POST'])  # 上传图片
@login_required
def upload():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail(message='File type not allowed!')
    filename = random_filename(f.filename)
    f.save(os.path.join(current_app.config['HY_UPLOAD_PATH'], filename))
    url = url_for('get_image', filename=filename)

    return upload_success(url=url)


@app.route('/admin/add_product', methods=['GET', 'POST'])  # 添加产品
@login_required
def add_product():
    form = AddProductForm()
    categories = Category.query.all()
    form.category.choices = [(category.id, category.name) for category in categories]

    if request.method == 'POST':
        if form.validate_on_submit():
            product = Product(
                name=form.name.data,
                category_id=form.category.data,
                price=form.price.data,
                material=form.material.data,
                level=form.level.data,
                oem=form.oem.data,
                content=form.content.data,
                clicks=0,
                timestamp=datetime.utcnow()
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


@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])  # 删除产品
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('删除成功.', 'success')
    return redirect(url_for('admin'))


@app.route('/delete_photo/<int:photo_id>', methods=['POST'])  # 删除图片
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    db.session.delete(photo)
    db.session.commit()
    flash('图片删除成功.', 'success')
    return redirect(url_for('edit_product', product_id=photo.product_id))


@app.route('/uploads/<path:filename>')  # 获得上传图片
def get_image(filename):
    return send_from_directory(current_app.config['HY_UPLOAD_PATH'], filename)


@app.route('/admin/login', methods=['GET', 'POST'])  # 登录
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.filter_by(username=username).first()
        if admin is None or not admin.validate_password(password):
            flash('用户名或密码错误.', 'warning')
            return redirect(url_for('login'))
        login_user(admin, remember)
        flash('欢迎回来.', 'success')
        return redirect(url_for('admin'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])  # 退出登录
@login_required
def logout():
    logout_user()
    flash('退出登录', 'success')
    return redirect(url_for('login'))


@app.route('/admin/websiteinfo', methods=['GET', 'POST'])  # 网站信息
def websiteinfo():
    websiteinfo = WebsiteInfo.query.first()
    form = WebsiteInfoForm()
    if form.validate_on_submit():
        websiteinfo.quick_information = form.quick_information.data
        websiteinfo.company_name = form.company_name.data
        websiteinfo.company_address = form.company_address.data
        websiteinfo.company_phone = form.company_phone.data
        websiteinfo.company_email = form.company_email.data
        websiteinfo.skype = form.skype.data
        websiteinfo.facebook = form.facebook.data
        websiteinfo.twitter = form.twitter.data
        websiteinfo.line = form.line.data
        db.session.commit()
        flash('修改成功.', 'success')
        return redirect(url_for('websiteinfo'))
    form.quick_information.data = websiteinfo.quick_information
    form.company_name.data = websiteinfo.company_name
    form.company_address.data = websiteinfo.company_address
    form.company_phone.data = websiteinfo.company_phone
    form.company_email.data = websiteinfo.company_email
    form.skype.data = websiteinfo.skype
    form.twitter.data = websiteinfo.twitter
    form.facebook.data = websiteinfo.facebook
    form.line.data = websiteinfo.line
    return render_template('websiteinfo.html', form=form)


@app.route('/admin/message', methods=['GET', 'POST'])
def message():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(page=page, per_page=current_app.config[
        'HY_MESSAGE_PER_PAGE'])
    messages = pagination.items
    return render_template('message.html', messages=messages, pagination=pagination)


@app.route('/delete_message/<int:message_id>', methods=['GET', 'POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('删除成功.', 'success')
    return redirect(url_for('message'))


@app.route('/admin/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        admin = Admin.query.get(current_user.id)
        if admin.validate_password(form.current_password.data):
            admin.set_password(form.new_password.data)
            db.session.commit()
            flash('密码修改成功,请重新登录.', 'success')
            logout_user()
            return redirect(url_for('login'))
        else:
            flash('原密码错误.', 'warning')
    return render_template('change_password.html', form=form)


@app.route('/admin/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = AddCategoryForm()
    categories = Category.query.all()
    if form.validate_on_submit():
        existing_category = Category.query.filter_by(name=form.name.data).first()
        if existing_category:
            flash('分类已存在.', 'warning')
            return redirect(url_for('add_category'))
        else:
            category = Category(name=form.name.data, description=form.description.data)
            db.session.add(category)
            db.session.commit()
            flash('添加成功.', 'success')
            return redirect(url_for('admin'))
    return render_template('add_category.html', form=form, categories=categories)


# 编辑分类
@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get(category_id)
    form = EditCategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('修改成功.', 'success')
        return redirect(url_for('admin'))
    form.name.data = category.name
    form.description.data = category.description
    return render_template('edit_category.html', form=form)


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
def website():
    from fakes import fake_website_info
    click.echo('Generating website info...')
    fake_website_info()

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

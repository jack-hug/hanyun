import random
from datetime import datetime

import click
from faker import Faker
from faker.providers import DynamicProvider

from app import Advantage, About, db, Product, Admin, WebsiteInfo

fake = Faker()

products = [
    'KOCUF',
    'KOCUM',
    'KPHF',
    'MTGL',
    'SCZA',
    'SCZAP',
    'SCZN',
    'SCZNP',
    'RCSUF',
    'RCSUM'
]  # 10 products


def fake_products():
    for product_name in products:
        if product_name == 'SCZAP':
            material = 'Brass+Graphite'
        else:
            material = 'S45C +Brass+Graphite'


        product = Product(
            name=product_name,
            price='0.0',
            material=material,
            level='High Quality',
            oem='Welcome',
            clicks=0,
            timestamp=datetime.now()
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
        timestamp=datetime.now()
    )
    db.session.add(about)
    db.session.commit()


def fake_advantage():
    advantage01 = Advantage(
        name='Big Stock',
        content='In order to shorten the delivery time, we always keep a large semi-stock and finished stock all over the year. Customer can get them in 5-7 days.',
        timestamp=datetime.now()
    )
    advantage02 = Advantage(
        name='100% Inspection',
        content='Quality is the first, so we will 100% inspect before shipping.',
        timestamp=datetime.now()
    )
    advantage03 = Advantage(
        name='Advanced Equipment',
        content='Our company has advanced processing equipment, a strict management system, and professional technical and production personnel.',
        timestamp=datetime.now()
    )
    advantage04 = Advantage(
        name='24-Hour Service',
        content='We can reply customers in 2 hours, and provide good after sales service.',
        timestamp=datetime.now()
    )
    db.session.add(advantage01)
    db.session.add(advantage02)
    db.session.add(advantage03)
    db.session.add(advantage04)
    db.session.commit()

def fake_website_info():
    website_info = WebsiteInfo(
        company_name='Shenzhen Hanyun Mold Co.,Ltd',
        company_address='Shenzhen, Guangdong, China',
        company_phone='+86',
        company_email='karen@hanyunmold.com',
        quick_information='Hanyun mold have more than 10 years of experience<br> in making slide core units.',
        facebook='karen',
        twitter='karen',
        skype='karen',
        line='karen',
    )
    db.session.add(website_info)
    db.session.commit()

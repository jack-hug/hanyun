import random
from datetime import datetime

import click
from faker import Faker
from faker.providers import DynamicProvider

from app import Advantage, About, db, Product, Admin

fake = Faker()

fake_products = DynamicProvider(
    provider_name='products',
    elements=[
        'KOCUF',
        'KOCUS',
        'KPHF',
        'MTGL',
        'SCZA',
        'SCZAP',
        'SCZNP',
        'SCZN'
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
            price='0.0',
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


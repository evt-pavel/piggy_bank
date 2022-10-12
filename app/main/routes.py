from app.main import main
from flask import render_template, request, url_for
from app.auth.routes import Product, ProductImage


@main.route('/')
@main.route('/index')
def index():
    avatar = '/posts/1/1.jpg'
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.timestamp.desc()).paginate(
        page, 3, False)
    next_url = url_for('main.index', page=products.next_num) \
        if products.has_next else None
    prev_url = url_for('main.index', page=products.prev_num) \
        if products.has_prev else None
    return render_template('index.html', products=products.items, avatar=avatar, next_url=next_url, prev_url=prev_url)

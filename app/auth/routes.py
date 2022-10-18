from app.auth import auth
from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.auth.forms import User, Registration, Login, UploadForm, EditProfile, CreateAd, Product, ProductImage
from app import db
from werkzeug.urls import url_parse
import os
import shutil  # этот модуль для удаления папки с файлами


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Не верный логин или пароль.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        flash('{} - Welcom to Piggy Bank'.format(user.username))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':   # нетлок - это грубоговоря наш домен. его не должно быть, т.к. путь должен быть относительный. Если он есть - это злоумышленники
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth.html', title='Sign_In', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('main.index'))
    form = Registration()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Are you registered! Sign in to continue!')
        return redirect(url_for('auth.login'))
    return render_template('registration.html', title='Registration', form=form)


@auth.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    avatar = '/avatars/' + str(user.id) + '.jpg'
    products = Product.query.filter_by(author=user).all()
    return render_template('profile.html', user=user, avatar=avatar, products=products)


@auth.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        form.file.data.save('app/static/avatars/' + str(current_user.id) + '.jpg')
        return redirect(url_for('.profile', username=current_user.username))
    return render_template('upload.html', form=form)


@auth.route('/change_info', methods=['GET', 'POST'])
@login_required
def change_info():
    form = EditProfile(current_user.username, current_user.email, current_user.phone)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Data has been changed!')
        return redirect(url_for('.profile', username=form.username.data))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    return render_template('edit_profile.html', form=form)


@auth.route('/create_ad', methods=['GET', 'POST'])
@login_required
def create_ad():
    form = CreateAd()
    if form.validate_on_submit():
        product = Product(product_name='product', product_description='post',
                          product_price=0, author=current_user)
        db.session.add(product)
        db.session.commit()

        product = Product.query.filter_by(product_name='product').first()
        product.product_name = form.name.data
        product.product_description = form.description.data
        product.product_price = form.price.data
        product.author = current_user
        db.session.add(product)
        db.session.commit()

        post_img_path = 'app/static/posts/{}/'.format(product.id)
        os.mkdir(post_img_path)
        count = 0
        for f in form.image.data:
            count += 1
            image = post_img_path + str(count) + '.jpg'
            f.save(image)

            product_image = ProductImage(image_url=image, product_id=product.id)
            db.session.add(product_image)
            db.session.commit()
        flash('Ad successfully created!!!')
        return redirect(url_for('.profile', username=current_user.username))
    return render_template('create_ad.html', form=form)


@auth.route('/open_product/<int:id>', methods=['GET', 'POST'])
def open_product(id):
    page = request.args.get('page', 1, type=int)
    product = Product.query.get(id)
    image = ProductImage.query.filter_by(product_id=id).paginate(page, 1, False)
    next_image = url_for('auth.open_product', id=product.id, page=image.next_num) \
        if image.has_next else None
    prev_image = url_for('auth.open_product', id=product.id, page=image.prev_num) \
        if image.has_prev else None
    return render_template('product.html', product=product,  image=image.items[0].image_url[11:],
                           next_image=next_image, prev_image=prev_image, user=product.author)


@auth.route('/product/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    product = Product.query.get(id)
    img_directory_path = 'app/static/posts/{}'.format(product.id)
    shutil.rmtree(img_directory_path)
    db.session.delete(product)
    db.session.commit()
    flash('You removed the ad!')
    return redirect(url_for('auth.profile', username=current_user.username))


@auth.route('/follow/product/<int:product_id>')
@login_required
def follow(product_id):
    product = Product.query.get(product_id)
    current_user.add_to_favourite(product)
    db.session.commit()
    flash('Product add to favourite')
    return redirect(url_for('auth.open_product', id=product_id))


@auth.route('/unfollow/product/<int:product_id>')
@login_required
def unfollow(product_id):
    product = Product.query.get(product_id)
    current_user.remove_from_favourite(product)
    db.session.commit()
    flash('Product remove from favourites')
    return redirect(url_for('.profile', username=current_user.username))
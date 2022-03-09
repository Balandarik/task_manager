import os
from flask import render_template, url_for, request, redirect, flash, session, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from task_manager import app, db, ALLOWED_EXTENSIONS
from task_manager.models import Users, Tasks
import traceback
from task_manager import mail
from flask_mail import Message
from task_manager import app

def send_email(recipients,template,title):
    if recipients!='Email не указан':
        with app.app_context():
            msg = Message(title)
            msg.recipients = recipients
            msg.sender = "no-reply@prz-task-manager.ru"
            msg.html = template
            mail.send(msg)

@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        return dict(viewed=Tasks.query.filter_by(name=Users.query.filter_by(user_id=current_user.user_id).first().name).filter_by(viewed=0).all())
    else: return []


@app.route('/customers')
@login_required
def customers():

    users=Users.query.order_by(Users.user_id.desc()).all()
    return render_template('customers.html',users=users)


@app.route('/')
def main():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    all_tasks=Tasks.query.filter(Tasks.visible==1).order_by(Tasks.date.desc()).all()
    users=Users.query.order_by(Users.user_id.desc()).all()
    return render_template('index.html',all_tasks=all_tasks,users=users)

@app.route('/create_task',methods=['POST','GET'])
@login_required
def create_task():
    users=Users.query.order_by(Users.name.desc()).all()
    if request.method=='POST':
        name=Users.query.filter_by(user_id=request.form.get('names')).first().name
        task_from_form=request.form['task']
        who=current_user.user_id
        task=Tasks(name=name, task=task_from_form,who=who)
        user=Users.query.filter_by(user_id=request.form.get('names')).first()
#         Отправка сообщения
        try:
            send_email(recipients=[user.email],
                    title='Новое задание',
                    template=render_template('new_task.html',task=task_from_form,user=name))
        except:pass

        try:

            db.session.add(task)
            db.session.commit()
            return redirect('/All_tasks')
        except:

            return redirect('/')
    else:

        return render_template('create_task.html',users=users)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')

@app.route('/All_tasks')
@login_required
def all_tasks():
    all_tasks=Tasks.query.filter_by(visible=True).order_by(Tasks.date.desc()).all()
    users=Users.query.order_by(Users.user_id.desc()).all()

    return render_template('all_tasks.html',all_tasks=all_tasks, users=users)

@app.route('/All_tasks/<int:id>', methods=['POST','GET'])
@login_required
def task_detail(id):
    if request.method=='POST':
        task_detail=Tasks.query.get(id)
        task_detail.check=True
        task_detail.report=request.form.get('report')
#         print(request.form.get('report'))
        file = request.files.get('file')
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        if request.files.get('file'):
            if file and allowed_file(file.filename):
                filename = secure_filename(str(task_detail.id)+' '+file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                task_detail.path=filename
        user=Users.query.filter_by(user_id=task_detail.who).first()

        try:
            db.session.commit()

        except:print('Error')
        try:
            send_email(recipients=[user.email],
                    title='Задание выполнено',
                    template=render_template('task_ready.html',task=task_detail,user=user))
        except:print('Error')
        return redirect('/All_tasks')

    else:

        task_detail=Tasks.query.get(id)
        users=Users.query.get(task_detail.who).name
        if task_detail.name==current_user.name:
            task_detail.viewed=1
            try:
                db.session.commit()
            except:return 'error'
        return render_template('task_detail.html',task_detail=task_detail,users=users)


@app.route('/All_tasks/<int:id>/delete')
@login_required
def task_delete(id):
    task_detail=Tasks.query.get_or_404(id)
    task_detail.visible=False
    try:
        db.session.commit()
        return redirect('/All_tasks')
    except:
        return traceback.format_exc()

@app.route('/customers/<int:id>')
@login_required
def user_detail(id):
    users=Users.query.get(id)
    return render_template('user_detail.html',user=users)

@app.route('/customers/<int:id>/delete')
@login_required
def user_delete(id):
    if current_user.role=='admin':
        user=Users.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
            return redirect('/admin')
        except:
            print(traceback.format_exc())
    else:return redirect('/All_tasks')

@app.route('/All_tasks/<int:id>/redact',methods=['POST','GET'])
@login_required
def task_redact(id):
    task_detail=Tasks.query.get(id)
    users=Users.query.order_by(Users.user_id.desc()).all()
    if request.method=='POST':
        task_detail.name=request.form['names']
        task_detail.task=request.form['task']

        try:
            db.session.commit()
            return redirect('/All_tasks')
        except:return 'error'
    else:
        return render_template('redact_task.html',task_detail=task_detail,users=users)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route('/media/<filename>')
def uploaded_file(filename):
    return send_from_directory('media/', filename)


@app.route('/All_tasks/<int:id>/confirm')
@login_required
def task_confirm(id):
    task_detail=Tasks.query.get(id)
    task_detail.check=True

    try:
        db.session.commit()
        return redirect('/All_tasks')
    except:return 'error'

@app.route('/All_tasks/<int:id>/retry')
@login_required
def task_retry(id):
    task_detail=Tasks.query.get(id)
    task_detail.check=False
    try:
        db.session.commit()
        return redirect('/All_tasks')
    except:return 'error'

@app.route('/register',methods=['GET','POST'])
def register():
    login=request.form.get('login')
    password=request.form.get('password')
    password2=request.form.get('password2')
    tel=request.form.get('tel')
    email=request.form.get('email')
    if request.method=="POST":
        if not (login or password or password2):
            flash('Заполните все поля')
        elif password != password2:
            flash('Пароли не совпадают')
        else:
            hash_password=generate_password_hash(password)
            new_user=Users(name=login,password=hash_password,tel=tel,email=email)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/login')
    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    login=request.form.get('user_name')
    password=request.form.get('password')
    if login and password:
        user=Users.query.filter_by(name=login).first()
        if user:

            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Неверный пароль')
                return redirect(url_for('login'))
#TODO сделать нормальный логин, что бы при неверном пароле не вываливалось
        else:return render_template('login.html')
    else:
        flash('Введите логин и пароль')
        return render_template('login.html')

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():

    users=Users.query.order_by(Users.user_id.desc()).all()
    return render_template('admin.html',users=users)

@app.after_request
def redirect_to_login(response):
    if response.status_code==401:
        return redirect(url_for('login')+'?next='+request.url)
    return response

def ints(i):
    return int(i)





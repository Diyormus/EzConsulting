from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course.db'
db = SQLAlchemy(app)
app.secret_key = 'super_secret_key'


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    teacher_img = db.Column(db.Text, nullable=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class PhoneNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    class_name = db.Column(db.String(80), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img_teacher_name = db.Column(db.String(100), nullable=False)

    img_teacher_data = db.Column(db.Text, nullable=False)
    img_course_data = db.Column(db.Text, nullable=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/courses', methods=['POST'])
def delete_course(course_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/login')

    course = Course.query.get(course_id)
    if not course:
        return 'Course not found'

    db.session.delete(course)
    db.session.commit()
    return redirect('/')


@app.route('/edit_course/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    course = Course.query.get(id)
    if course:
        if request.method == 'POST':
            class_name = request.form['class_name']
            course_name = request.form['course_name']
            short_description = request.form['short_description']
            price = request.form['price']
            teacher_name = request.form['teacher_name']
            teacher_img = request.files['teacher_img']
            course_img = request.files['course_img']

            course.class_name = class_name
            course.course_name = course_name
            course.short_description = short_description
            course.price = price
            course.img_teacher_name = teacher_name

            if teacher_img:
                course.img_teacher_data = b64encode(teacher_img.stream.read()).decode('utf-8')
            if course_img:
                course.img_course_data = b64encode(course_img.stream.read()).decode('utf-8')

            db.session.commit()

            return jsonify({'message': 'Course edited successfully'}), 200
        else:

            return render_template('edit_course.html', course=course)
    else:

        return jsonify({'error': 'Course not found'}), 404


@app.route('/admin', methods=['GET'])
def admin():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/login')
    if request.method == 'POST':
        # Handle POST request if needed
        pass
    else:
        phone_numbers = PhoneNumber.query.all()
        return render_template('admin.html', phone_numbers=phone_numbers)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/create_course', methods=['POST', 'GET'])
def create_course():
    print(request.form)
    if request.method == 'POST':
        class_name = request.form['class_name']
        course_name = request.form['course_name']
        short_description = request.form['short_description']
        price = request.form['price']
        teacher_name = request.form['teacher_name']
        teacher_img = request.files['teacher_img']
        course_img = request.files['course_img']
        course = Course(class_name=class_name,
                        course_name=course_name,
                        img_course_data=b64encode(course_img.stream.read()).decode('utf-8'),
                        short_description=short_description,
                        price=price,
                        img_teacher_name=teacher_name,
                        img_teacher_data=b64encode(teacher_img.stream.read()).decode('utf-8'))

        db.session.add(course)
        db.session.commit()

        return redirect('/')
    print(request.form)

    return render_template('create_course.html')


@app.route('/create_teacher', methods=['POST', 'GET'])
def create_teacher():
    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        subject = request.form['subject']
        short_description = request.form['short_description']
        teacher_img = request.files['teacher_img']

        teacher = Teacher(teacher_name=teacher_name,
                          subject=subject,
                          short_description=short_description,
                          teacher_img=b64encode(teacher_img.stream.read()).decode('utf-8'))

        db.session.add(teacher)
        db.session.commit()

        return redirect('/')

    return render_template('create_teacher.html')


@app.route('/')
def index():
    course = Course.query.order_by(Course.price).all()
    teacher = Teacher.query.order_by(Teacher.teacher_name).all()
    if request.method == 'POST':
        number = request.form['number']
        existing_number = PhoneNumber.query.filter_by(number=number).first()
        if not existing_number:
            new_number = PhoneNumber(number=number)
            db.session.add(new_number)
            db.session.commit()
    return render_template('index.html', course=course, teacher=teacher)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route('/courses', methods=['GET'])
def courses():
    course = Course.query.order_by(Course.price).all()
    return render_template('courses.html', course=course)


@app.route('/pricing', methods=['GET'])
def pricing():
    return render_template('pricing.html')


@app.route('/trainers', methods=['GET'])
def trainers():
    teacher = Teacher.query.order_by(Teacher.teacher_name).all()
    return render_template('trainers.html', teacher=teacher)


with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password='admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run()

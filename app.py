from base64 import b64encode

from flask import Flask, jsonify, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course.db'
app.secret_key = 'super_secret_key'

db = SQLAlchemy(app)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    class_name = db.Column(db.String(80), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img_teacher_name = db.Column(db.String(100), nullable=False)

    img_teacher_data = db.Column(db.Text, nullable=False)
    img_course_data = db.Column(db.Text, nullable=False)


class PhoneNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    teacher_img = db.Column(db.Text, nullable=False)


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


@app.route('/admin', methods=['GET'])
def admin():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/login')

    phone_numbers = PhoneNumber.query.all()

    return render_template('admin.html', phone_numbers=phone_numbers)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        is_admin = Admin.query.filter_by(username=username, password=password).first()

        if is_admin:
            session['logged_in'] = True

            return redirect('/admin')

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()

    return redirect('/')


@app.route('/create_course', methods=['POST', 'GET'])
def create_course():
    if ('logged_in' not in session) or (not session['logged_in']):
        return jsonify({'error': 'Unauthorized access'}), 401

    if request.method == 'POST':
        class_name = request.form['class_name']
        course_name = request.form['course_name']
        short_description = request.form['short_description']
        price = request.form['price']
        img_teacher_name = request.form['teacher_name']

        teacher_img = request.files['teacher_img']
        course_img = request.files['course_img']

        course = Course(class_name=class_name,
                        course_name=course_name,
                        img_course_data=b64encode(course_img.stream.read()).decode('utf-8'),
                        short_description=short_description,
                        price=price,
                        img_teacher_name=img_teacher_name,
                        img_teacher_data=b64encode(teacher_img.stream.read()).decode('utf-8'))

        db.session.add(course)
        db.session.commit()

        return redirect('/')

    return render_template('create_course.html')


@app.route('/create_teacher', methods=['POST', 'GET'])
def create_teacher():
    if ('logged_in' not in session) or (not session['logged_in']):
        return jsonify({'error': 'Unauthorized access'}), 401

    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        subject = request.form['subject']
        short_description = request.form['short_description']

        teacher_img = request.files.get('teacher_img', None)

        teacher = Teacher(teacher_name=teacher_name,
                          subject=subject,
                          short_description=short_description,
                          teacher_img=b64encode(teacher_img.stream.read()).decode('utf-8'))

        db.session.add(teacher)
        db.session.commit()

        return redirect('/')

    return render_template('create_teacher.html')


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


@app.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.query.get(course_id)

    if course:
        if request.method == 'POST':
            class_name = request.form['class_name']
            course_name = request.form['course_name']
            short_description = request.form['short_description']
            price = request.form['price']
            img_teacher_name = request.form['teacher_name']

            teacher_img = request.files.get('teacher_img', None)
            course_img = request.files.get('course_img', None)

            course.class_name = class_name
            course.course_name = course_name
            course.short_description = short_description
            course.price = price
            course.img_teacher_name = img_teacher_name

            if teacher_img:
                course.img_teacher_data = b64encode(teacher_img.stream.read()).decode('utf-8')

            if course_img:
                course.img_course_data = b64encode(course_img.stream.read()).decode('utf-8')

            db.session.commit()

            return redirect("/courses"), 200

        return render_template('edit_course.html', course=course)

    return jsonify({'error': 'Course not found'}), 404


@app.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)

    if teacher:
        if request.method == 'POST':
            teacher_name = request.form['teacher_name']
            subject = request.form['subject']
            short_description = request.form['short_description']

            teacher_img = request.files.get('teacher_img', None)

            teacher.teacher_name = teacher_name
            teacher.subject = subject
            teacher.short_description = short_description
            teacher.teacher_img = teacher_img

            if teacher_img:
                teacher.teacher_img = b64encode(teacher_img.stream.read()).decode('utf-8')

            db.session.commit()

            return redirect("/trainers"), 200

        return render_template('edit_teachers.html', teacher=teacher)

    return jsonify({'error': 'Course not found'}), 404


@app.route('/delete_course/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    if ('logged_in' not in session) or (not session['logged_in']):
        return jsonify({'error': 'Unauthorized access'}), 401

    course = Course.query.get(course_id)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    db.session.delete(course)
    db.session.commit()

    return jsonify({'message': 'Course deleted successfully'}), 200


@app.route('/delete_teacher/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    if ('logged_in' not in session) or (not session['logged_in']):
        return jsonify({'error': 'Unauthorized access'}), 401

    teacher = Teacher.query.get(teacher_id)

    if not teacher:
        return jsonify({'error': 'Course not found'}), 404

    db.session.delete(teacher)
    db.session.commit()

    return jsonify({'message': 'Course deleted successfully'}), 200


with app.app_context():
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password='admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run()

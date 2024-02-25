from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
db = SQLAlchemy(app)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(80), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    teacher_name = db.Column(db.String(80), nullable=False)
    teacher_img = db.Column(db.Text, unique=True, nullable=False)
    course_img = db.Column(db.Text, unique=True, nullable=False)
    mimetype_teacher = db.Column(db.Text(), nullable=False)
    mimetype_course = db.Column(db.Text(), nullable=False)
    isActive = db.Column(db.Boolean, default=True)


class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_img = db.Column(db.Text, unique=True, nullable=False)
    course_img = db.Column(db.Text, unique=True, nullable=False)
    mimetype_teacher = db.Column(db.Text, nullable=False)
    mimetype_course = db.Column(db.Text, nullable=False)


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
        filename_teacher = secure_filename(teacher_img.filename)
        filename_course = secure_filename(course_img.filename)
        mimetype_teacher = teacher_img.mimetype_teacher
        mimetype_course = course_img.mimetype_course
        img_teacher = Img(img=teacher_img.read(), mimetype=mimetype_teacher, name=filename_teacher)
        img_course = Img(img=course_img.read(), mimetype=mimetype_course, name=filename_course)

        course = Course(class_name=class_name, course_name=course_name,
                        short_description=short_description, price=price, teacher_name=teacher_name,
                        img_teacher=img_teacher, img_course=img_course)

        # try:
        #     db.session.add(course)
        #     db.session.commit()
        #     return redirect('/')
        #
        # except:
        #     return "Error, Something went wrong"

    else:
        return render_template('create_course.html')


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'GET':
        return render_template('about.html')
    else:
        return print("Error")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@app.route('/courses', methods=['GET', 'POST'])
def courses():
    course = Course.query.order_by(Course.price).all()
    return render_template('courses.html', course=course)


@app.route('/events', methods=['GET', 'POST'])
def events():
    return render_template('events.html')


@app.route('/pricing', methods=['GET', 'POST'])
def pricing():
    return render_template('pricing.html')


@app.route('/trainers', methods=['GET', 'POST'])
def trainers():
    return render_template('trainers.html')


@app.route('/course-details', methods=['GET', 'POST'])
def course_details():
    return render_template('course-details.html')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()

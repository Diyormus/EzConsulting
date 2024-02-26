from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import secure_filename
from base64 import b64encode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
db = SQLAlchemy(app)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    class_name = db.Column(db.String(80), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    img_teacher_name = db.Column(db.String(100), nullable=False)
    img_teacher_data = db.Column(db.Text, nullable=False)

    img_course_name = db.Column(db.String(100), nullable=False)
    img_course_data = db.Column(db.Text, nullable=False)

    mimetype_teacher_img = db.Column(db.Text(), nullable=False)
    mimetype_course_img = db.Column(db.Text(), nullable=False)

    isActive = db.Column(db.Boolean, default=True)


# class Img(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     img_name = db.Column(db.Text, nullable=False)
#     img_data = db.Column(db.Text, nullable=False)
#     mimetype = db.Column(db.Text, nullable=False)


@app.route('/create_course', methods=['POST', 'GET'])
def create_course():
    if request.method == 'POST':
        class_name = request.form['class_name']
        course_name = request.form['course_name']
        short_description = request.form['short_description']
        price = request.form['price']
        teacher_name = request.form['teacher_name']
        print(request.files)
        teacher_img = request.files['teacher_img']
        course_img = request.files['course_img']
        # filename_teacher = secure_filename(teacher_img.filename)
        # filename_course = secure_filename(course_img.filename)
        # filename_teacher = teacher_img.filename
        # filename_course = course_img.filename
        mimetype_teacher = teacher_img.mimetype
        mimetype_course = course_img.mimetype

        # img_teacher = Img(img_data=teacher_img.stream.read(), img_name=filename_teacher, mimetype=mimetype_teacher)
        # img_course = Img(img_data=course_img.stream.read(), img_name=filename_course, mimetype=mimetype_course)

        course = Course(class_name=class_name,
                        img_course_name=course_name,
                        img_course_data=b64encode(course_img.stream.read()).decode('utf-8'),
                        short_description=short_description,
                        price=price,
                        img_teacher_name=teacher_name,
                        img_teacher_data=b64encode(teacher_img.stream.read()).decode('utf-8'),
                        mimetype_teacher_img=mimetype_teacher,
                        mimetype_course_img=mimetype_course)

        db.session.add(course)
        db.session.commit()

        return redirect('/')

    return render_template('create_course.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route('/courses', methods=['GET'])
def courses():
    course = Course.query.order_by(Course.price).all()
    from pprint import pprint
    pprint(course[0].img_teacher_data)
    return render_template('courses.html', course=course)


@app.route('/events', methods=['GET'])
def events():
    return render_template('events.html')


@app.route('/pricing', methods=['GET'])
def pricing():
    return render_template('pricing.html')


@app.route('/trainers', methods=['GET'])
def trainers():
    return render_template('trainers.html')


@app.route('/course-details', methods=['GET'])
def course_details():
    return render_template('course-details.html')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()

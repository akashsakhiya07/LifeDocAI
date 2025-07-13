from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject
import os
import csv

app = Flask(__name__)
app.secret_key = 'Password123'  # Change this to a secure key in production

# Config
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'users.db')
db = SQLAlchemy(app)

# Email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'xyz@gmail.com'
app.config['MAIL_PASSWORD'] = '[Your mail password]'
mail = Mail(app)

# DB Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_filename = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    dob = db.Column(db.String(20))
    aadhaar = db.Column(db.String(20))

# ✅ PDF Generator
def generate_pdf(user):
    user_data = {
        'Name': user.name,
        'Email': user.email,
        'Phone': user.phone
    }

    template_path = 'form_template.pdf'
    output_folder = 'filled_forms'
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f'filled_form_{user.id}.pdf')

    template_pdf = PdfReader(template_path)
    annotations = template_pdf.pages[0]['/Annots']

    for annotation in annotations:
        if annotation['/Subtype'] == '/Widget':
            field = annotation.get('/T')
            if field:
                field_name = field[1:-1]
                if field_name in user_data:
                    annotation.update(PdfDict(V='{}'.format(user_data[field_name])))

    if template_pdf.Root.AcroForm:
        template_pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))

    PdfWriter(output_path, trailer=template_pdf).write()

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    dob = request.form['dob']
    aadhaar = request.form['aadhaar']

    photo = request.files.get('photo')
    photo_filename = None
    if photo and photo.filename:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        photo_filename = f"{name.replace(' ', '_')}_{photo.filename}"
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    user = User(name=name, email=email, phone=phone, dob=dob, aadhaar=aadhaar, photo_filename=photo_filename)
    db.session.add(user)
    db.session.commit()

    generate_pdf(user)

    # 📧 Email to user
    pdf_path = os.path.join('filled_forms', f'filled_form_{user.id}.pdf')
    user_msg = Message('Your LifeDoc Form is Ready', sender='akashsakhiya12@gmail.com', recipients=[user.email])
    user_msg.body = f"Hi {user.name},\n\nPlease find attached your filled LifeDoc form.\n\nRegards,\nLifeDoc AI"
    with app.open_resource(pdf_path) as fp:
        user_msg.attach(f'filled_form_{user.id}.pdf', 'application/pdf', fp.read())
    mail.send(user_msg)

    # 📧 Email to Admin
    admin_msg = Message('New LifeDocAI Submission Received!', sender='akashsakhiya12@gmail.com', recipients=['akashsakhiya12@gmail.com'])
    admin_msg.body = f"""
New LifeDocAI submission received!

Name: {user.name}
Email: {user.email}
Phone: {user.phone}
DOB: {user.dob}
Aadhaar: {user.aadhaar}
"""
    with app.open_resource(pdf_path) as fp:
        admin_msg.attach(f'filled_form_{user.id}.pdf', 'application/pdf', fp.read())
    mail.send(admin_msg)

    return render_template('success.html', user_id=user.id, preview_url=url_for('preview', user_id=user.id), photo_filename=photo_filename)

# 🔒 Admin Login
ADMIN_CODE = 'password123'  # Change this to a secure code in production

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        code = request.form.get('code')
        if code == ADMIN_CODE:
            session['admin'] = True
            return redirect(url_for('view_users'))
        else:
            flash('Invalid password', 'danger')
    return render_template('admin_login.html')

# 👁️ View Users
@app.route('/view_users')
def view_users():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('view_users.html', users=users)

# 🗑️ Delete User
@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        pdf_path = os.path.join('filled_forms', f'filled_form_{user.id}.pdf')
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('view_users'))

# 🔓 Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# 🖼️ Serve Uploaded Photo
@app.route('/uploads/<filename>')
def uploaded_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 👁️ Preview PDF
@app.route('/preview/<int:user_id>')
def preview(user_id):
    return send_from_directory('filled_forms', f'filled_form_{user_id}.pdf', as_attachment=False)

# 📥 Download PDF
@app.route('/download/<int:user_id>')
def download(user_id):
    return send_from_directory('filled_forms', f'filled_form_{user_id}.pdf', as_attachment=True)

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)

# 📊 Export CSV
@app.route('/export_csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    csv_path = os.path.join('filled_forms', 'lifedoc_users.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'DOB', 'Aadhaar'])
        for u in users:
            writer.writerow([u.id, u.name, u.email, u.phone, u.dob, u.aadhaar])
    return send_from_directory('filled_forms', 'lifedoc_users.csv', as_attachment=True)

# ✏️ Edit User
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.dob = request.form['dob']
        user.aadhaar = request.form['aadhaar']

        photo = request.files.get('photo')
        if photo and photo.filename:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            photo_filename = f"{user.name.replace(' ', '_')}_{photo.filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            user.photo_filename = photo_filename

        db.session.commit()
        generate_pdf(user)
        return redirect(url_for('view_users'))

    return render_template('edit_user.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)

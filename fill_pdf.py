from pdfrw import PdfReader, PdfWriter, PdfDict
from app import app, db, User

# Activate Flask app context
app.app_context().push()

# Get the latest user entry
latest_user = User.query.order_by(User.id.desc()).first()

# Create dictionary from database
user_data = {
    'Name': latest_user.name,
    'Email': latest_user.email,
    'Phone': latest_user.phone
}

# PDF file paths
template_path = 'form_template.pdf'   # ya 'form_template.pdf.pdf' if not renamed
output_path = 'filled_form.pdf'

# Read and fill the template PDF
template_pdf = PdfReader(template_path)
annotations = template_pdf.pages[0]['/Annots']

for annotation in annotations:
    if annotation['/Subtype'] == '/Widget':
        field = annotation.get('/T')
        if field:
            field_name = field[1:-1]  # remove brackets
            if field_name in user_data:
                annotation.update(
                    PdfDict(V='{}'.format(user_data[field_name]))
                )

# Save the filled PDF
PdfWriter(output_path, trailer=template_pdf).write()
print("✅ Form filled with latest user from DB!")

from pdfrw import PdfReader, PdfWriter, PdfDict
from app import app, db, User
import os

# Activate Flask app context
app.app_context().push()

# Get all users from DB
all_users = User.query.all()

template_path = 'form_template.pdf'  # ya 'form_template.pdf.pdf'

# Output folder bana lo agar nahi hai to
output_folder = 'filled_forms'
os.makedirs(output_folder, exist_ok=True)

for user in all_users:
    user_data = {
        'Name': user.name,
        'Email': user.email,
        'Phone': user.phone
    }

    # Read template
    template_pdf = PdfReader(template_path)
    annotations = template_pdf.pages[0]['/Annots']

    for annotation in annotations:
        if annotation['/Subtype'] == '/Widget':
            field = annotation.get('/T')
            if field:
                field_name = field[1:-1]
                if field_name in user_data:
                    annotation.update(
                        PdfDict(V='{}'.format(user_data[field_name]))
                    )

    # Output path for this user
    output_path = os.path.join(output_folder, f'filled_form_{user.id}.pdf')

    # Write filled PDF
    PdfWriter(output_path, trailer=template_pdf).write()

print(f"✅ {len(all_users)} PDFs generated in '{output_folder}' folder.")

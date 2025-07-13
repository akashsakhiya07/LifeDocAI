from app import db, User

users = User.query.all()

for user in users:
    print(f"Name: {user.name}, Email: {user.email}, Phone: {user.phone}, DOB: {user.dob}, Aadhaar: {user.aadhaar}")

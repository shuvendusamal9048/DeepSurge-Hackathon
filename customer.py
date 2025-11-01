from db import session, FileMeta, User

# Check all users
users = session.query(User).all()
for u in users:
    print(f"User: {u.username}, Password Hash: {u.password}")

# Check all uploaded files
files = session.query(FileMeta).all()
for f in files:
    print(f"File: {f.filename}, Uploaded By: {f.uploaded_by}, Date: {f.uploaded_at}, Rows: {f.rows}, Columns: {f.cols}")

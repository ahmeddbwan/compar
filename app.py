from flask import Flask, render_template, request, flash
from flask_dropzone import Dropzone
import os
import pandas as pd
import sqlite3

app = Flask(__name__)
dropzone = Dropzone(app)  # Initialize Dropzone extension

# Flask config
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'UPLOAD_FOLDER')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Dropzone config
app.config['DROPZONE_UPLOAD_MULTIPLE'] = False
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.xlsx'
app.config['DROPZONE_MAX_FILE_SIZE'] = 10  # in MB
app.config['DROPZONE_UPLOAD_ON_CLICK'] = True
app.config['DROPZONE_DEFAULT_MESSAGE'] = "Drop your Excel file here or click to upload"

# Function to create table if it doesn't exist
def create_table():
    try:
        # Connect to SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                device_name TEXT,
                sim_name TEXT,
                sim_number TEXT,
                sim_location TEXT,
                password TEXT,
                balance TEXT,
                sim_type TEXT,
                sim_status TEXT
            )
        ''')

        # Commit and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")

# Function to insert data into the database
def insert_data_to_db(data):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
        cursor = conn.cursor()

        # Insert data into the database
        cursor.executemany('''
            INSERT INTO file_data (
                company_name, device_name, sim_name, sim_number, 
                sim_location, password, balance, sim_type, sim_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)

        # Commit and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error inserting data into database: {e}")

# Route to handle file upload
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file is uploaded through Dropzone
        file = request.files.get('file')
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Create table in the database
            create_table()

            try:
                # Read the Excel file using pandas
                df = pd.read_excel(filepath)

                # Extract relevant columns from the Excel file
                data = df[['الشركة', 'اسم الجهاز', 'اسم الشريحة', 'رقم الشريحة', 'موقع الشريحة', 'كلمة السر', 'الرصيد', 'نوع الشريحة', 'حالة الشريحة']].values.tolist()

                # Insert data into the database
                insert_data_to_db(data)

                flash('✅ File uploaded and data inserted successfully into the database!')
            except Exception as e:
                flash(f'❌ Error processing file: {str(e)}')
        else:
            flash('❌ No file selected.')
    return render_template('index.html')

# Route to display uploaded data (you can change this as per your need)
@app.route('/view_data')
def view_data():
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM file_data')
        rows = cursor.fetchall()
        conn.close()
        return render_template('view_data.html', rows=rows)
    except Exception as e:
        flash(f'❌ Error fetching data: {str(e)}')
        return render_template('view_data.html', rows=[])

if __name__ == '__main__':
    app.run(debug=True)

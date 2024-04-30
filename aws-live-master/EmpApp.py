from flask import Flask, render_template, request
from pymysql import connect, Error
import boto3
from config import custombucket, customregion, customhost, customuser, custompass, customdb

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    try:
        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        emp_image_file = request.files['emp_image_file']

        # Connect to the MySQL database
        conn = connect(host=customhost, user=customuser, password=custompass, database=customdb)
        cursor = conn.cursor()

        # Insert data into the database
        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        conn.commit()

        # Upload image file to S3
        s3 = boto3.client('s3')
        s3_key = f"emp-id-{emp_id}_image_file"
        s3.upload_fileobj(emp_image_file, custombucket, s3_key)

        # Get the URL of the uploaded image
        object_url = f"https://{custombucket}.s3.{customregion}.amazonaws.com/{s3_key}"

        cursor.close()
        conn.close()

        return render_template('AddEmpOutput.html', name=f"{first_name} {last_name}", image_url=object_url)

    except Error as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

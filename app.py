from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import os
from werkzeug.utils import secure_filename
import xlsxwriter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_regression_chart(df):
    X = df['YearsExperience'].values.reshape(-1, 1)
    y = df['Salary'].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    predicted_salary = model.predict(X)
    
    # Get coefficients of the regression line
    slope = model.coef_[0][0]
    intercept = model.intercept_[0]
    
    # Plotting
    plt.scatter(X, y, color='blue')
    plt.plot(X, predicted_salary, color='red')
    plt.xlabel('Years of Experience')
    plt.ylabel('Salary')
    
    # Adding the equation of the line to the plot
    equation = f'y = {slope:.2f}x + {intercept:.2f}'
    plt.title(f'Regression Analysis: Salary vs. Years of Experience\n{equation}')
    plt.grid(True)
    
    # Saving the plot
    chart_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'regression_analysis.png')
    plt.savefig(chart_file_path)
    plt.close()
    
    return chart_file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        reg_number = request.form['reg_number']
        name = request.form['name']
        
        return redirect(url_for('analyze', filename=filename, reg_number=reg_number, name=name))

@app.route('/analyze/<filename>/<reg_number>/<name>')
def analyze(filename, reg_number, name):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(file_path)
    
    chart_file_path = generate_regression_chart(df)
    
    output_filename = f"{name}_{reg_number}.xlsx"
    output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        workbook = writer.book
        worksheet = writer.sheets['Data']
        worksheet.insert_image('E2', chart_file_path)
    
    return send_file(output_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

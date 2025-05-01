import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from flask import Flask, render_template, request, flash, redirect, url_for

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key_here'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Home route for file upload
@app.route('/')
def upload_file():
    return render_template('upload.html')

# Handle file upload and process data
@app.route('/upload', methods=['POST'])
def handle_upload():
    file = request.files['file']
    if file:
        if not file.filename.endswith('.csv'):
            flash("Invalid file type. Please upload a CSV file.", 'danger')
            return redirect(url_for('upload_file'))

        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            # Read the dataset
            data = pd.read_csv(filepath)

            # Check if the dataset is empty
            if data.empty:
                flash("Uploaded CSV file is empty.", 'warning')
                return redirect(url_for('upload_file'))

            # Identify numeric columns
            numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
            non_numeric_cols = data.select_dtypes(exclude=['float64', 'int64']).columns

            # Prepare summary for numeric columns
            numeric_summary = {}
            if not numeric_cols.empty:
                numeric_summary = data[numeric_cols].describe().T[['mean', 'min', 'max', 'count']].to_dict('index')

            # Prepare summary for non-numeric columns (categorical data)
            non_numeric_summary = {}
            if not non_numeric_cols.empty:
                non_numeric_summary = data[non_numeric_cols].describe().T[['top', 'freq']].to_dict('index')

            # Generate charts for numeric data (if any)
            charts = []
            if not numeric_cols.empty:
                for col in numeric_cols:
                    fig, ax = plt.subplots()
                    sns.histplot(data[col], kde=True, ax=ax)
                    ax.set_title(f'{col} Distribution')
                    img = BytesIO()
                    fig.savefig(img, format='png')
                    img.seek(0)
                    charts.append(base64.b64encode(img.getvalue()).decode('utf-8'))

            # Render the dashboard page
            return render_template('dashboard.html',
                                   numeric_summary=numeric_summary,
                                   non_numeric_summary=non_numeric_summary,
                                   charts=charts)

        except Exception as e:
            flash(f"Error processing file: {str(e)}", 'danger')
            return redirect(url_for('upload_file'))

    flash("No file uploaded.", 'danger')
    return redirect(url_for('upload_file'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

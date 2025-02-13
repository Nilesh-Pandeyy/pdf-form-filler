from flask import Flask, render_template, request, send_file
import os
import zipfile
from datetime import datetime
from pdf_filler import fill_pdf 
import pandas as pd
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
BULK_FOLDER = 'bulk_uploads'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(BULK_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/fill-pdf', methods=['POST'])
def process_pdf():
    # Check upload type
    upload_type = request.form.get('upload_type', 'single')
    
    # Get the input PDF file
    input_pdf = request.files['input_pdf']
    if not input_pdf:
        return "No PDF template uploaded", 400

    # If it's a bulk upload, process bulk PDF
    if upload_type == 'bulk':
        # Check if bulk CSV is present for bulk upload
        if 'bulk_csv' not in request.files or not request.files['bulk_csv']:
            return "No CSV file uploaded for bulk processing", 400
        return process_bulk_pdf()
    
    # Otherwise, process single PDF
    return process_single_pdf()

def process_single_pdf():
    # Get the input PDF file
    input_pdf = request.files['input_pdf']
    if not input_pdf:
        return "No file uploaded", 400

    # Get form data
    form_data = {
        'day': request.form.get('day', ''),
        'monthx': request.form.get('month', ''),  # Changed from 'monthx' to 'month'
        'company_address': request.form.get('company_address', ''),
        'employee_name': request.form.get('employee_name', ''),
        'employee_address': request.form.get('employee_address', ''),
        'company_rep_name': request.form.get('company_rep_name', ''),
        'designation': request.form.get('designation', ''),
        'witness_name': request.form.get('witness_name', ''),
        'current_date': request.form.get('current_date', datetime.now().strftime("%d/%m/%Y"))
    }
    
    # Save the uploaded PDF
    input_path = os.path.join(UPLOAD_FOLDER, 'input.pdf')
    input_pdf.save(input_path)
    
    # Generate output filename 
    employee_name = form_data['employee_name'].replace(' ', '_')
    output_filename = f"{employee_name}_Non_disclosure.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Fill the PDF with the form data
    fill_pdf(input_path, output_path, form_data)
    
    # Send the filled PDF back to user
    return send_file(output_path, as_attachment=True, download_name=output_filename)
def process_bulk_pdf():
    # Get the input PDF template
    input_pdf = request.files['input_pdf']
    if not input_pdf:
        return "No PDF template uploaded", 400

    # Get the CSV file with employee data
    bulk_csv = request.files['bulk_csv']
    if not bulk_csv:
        return "No CSV file uploaded", 400

    # Save the PDF template
    input_path = os.path.join(UPLOAD_FOLDER, 'input.pdf')
    input_pdf.save(input_path)

    # Read the CSV file
    try:
        df = pd.read_csv(bulk_csv)
    except Exception as e:
        return f"Error reading CSV: {str(e)}", 400

    # Prepare a zip file for output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Bulk_Non_Disclosure_{timestamp}.zip"
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)

    # Create a zip file to store all PDFs
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Iterate through each row in the CSV
        for index, row in df.iterrows():
            # Prepare form data from CSV row
            form_data = {
                'day': row.get('day', ''),
                'monthx': row.get('month', ''),
                'year': row.get('year', ''),
                'company_address': row.get('company_address', ''),
                'employee_name': row.get('employee_name', ''),
                'employee_address': row.get('employee_address', ''),
                'company_rep_name': row.get('company_rep_name', ''),
                'designation': row.get('designation', ''),
                'witness_name': row.get('witness_name', ''),
                'employee_signature': row.get('employee_name', ''),
                'current_date': row.get('current_date', datetime.now().strftime("%d/%m/%Y"))
            }

            # Generate output filename for each employee
            employee_name = form_data['employee_name'].replace(' ', '_')
            output_filename = f"{employee_name}_Non_disclosure.pdf"
            
            # Prepare temporary output path
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            # Fill the PDF with the form data
            fill_pdf(input_path, output_path, form_data)
            
            # Add the filled PDF to the zip file
            zipf.write(output_path, arcname=output_filename)
            
            # Optional: Remove the individual PDF after adding to zip
            os.remove(output_path)

    # Send the zip file back to user
    return send_file(zip_path, as_attachment=True, download_name=zip_filename)

@app.route('/download-sample-csv')
def download_sample_csv():
    # Path to the sample CSV
    sample_csv_path = os.path.join(os.path.dirname(__file__), 'sample_employee_data.csv')
    
    # Ensure the sample CSV exists
    if not os.path.exists(sample_csv_path):
        # Create the sample CSV if it doesn't exist
        sample_data = [
            "day,month,year,company_address,employee_name,employee_address,company_rep_name,designation,witness_name,current_date",
            '06,February,2025,"S-12, Janta Market, Rajouri Garden, New Delhi-110059",Nilesh Pandey,"Andheri east, Mumbai-400072",Madhurima,HR Manager,Ayan Hazra,2025-02-06',
            '07,March,2025,"Corporate Office, Tower A, Bangalore-560001",Rajesh Kumar,"Koramangala, Bangalore-560095",Priya Sharma,Senior HR,Vikram Singh,2025-03-07',
            '15,April,2025,"Tech Park, Sector 5, Hyderabad-500032",Sneha Reddy,"Gachibowli, Hyderabad-500075",Rahul Mehta,Operations Head,Sameer Khan,2025-04-15',
            '22,May,2025,"Cyber City, Gurugram-122002",Amit Sharma,"DLF Phase 2, Gurugram-122010",Neha Kapoor,Talent Acquisition,Rohan Desai,2025-05-22'
        ]
        
        with open(sample_csv_path, 'w', newline='\n') as f:
            f.write('\n'.join(sample_data))
    
    # Send the file for download
    return send_file(sample_csv_path, 
                     as_attachment=True, 
                     download_name='sample_employee_data.csv')

if __name__ == '__main__':
    app.run(debug=True)
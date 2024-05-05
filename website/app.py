import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import tempfile
import PyPDF2
import google.generativeai as genai

with tempfile.TemporaryDirectory() as temp_dir:
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = temp_dir

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            file = request.files['file']
            custom_prompt = request.form['custom_prompt']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Process the file here using the file_path
                # ... (your file processing logic)

                # Extract text from the uploaded PDF
                text = extract_text_from_pdf(file_path)

                # Generate summary from the extracted text
                summary = generate_summary(text, custom_prompt)

                # Return success message with the summary
                return render_template('success.html', summary=summary)
        return render_template('index.html')

    # Function to extract text from a PDF file
    def extract_text_from_pdf(pdf_file_path):
        text = ""
        with open(pdf_file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text

    # Function to generate a summary from extracted text
    def generate_summary(text, custom_prompt):
        # Initialize the GenerativeAI model
        txt_model = genai.GenerativeModel('gemini-pro')

        # Give the prompt to the model and get the response
        response = txt_model.generate_content(
            f"{custom_prompt}{text}")

        summary = response.text
        return summary

    @app.route('/success')
    def success():
        return render_template('success.html')  # Display the summary here

    if __name__ == '__main__':
        app.run(debug=True, port=8000)

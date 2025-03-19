import urllib.request
import urllib.error
import subprocess
import tempfile
import os
import fitz  # PyMuPDF
from flask import Flask, request, send_file, render_template, abort, Response
from io import BytesIO

app = Flask(__name__)

# Configure wkhtmltopdf path
WKHTMLTOPDF_PATH = "/usr/bin/wkhtmltopdf"  # Updated path for Linux

def retrieve_informe_as_pdf(ref_catastral: str) -> bytes:
    """
    Given a parcel reference (the string between 'parcelas/' and '/informeHTML'),
    this function fetches the HTML report from the Consell de Mallorca API and
    renders it into a PDF. It returns the PDF as bytes.

    Requirements:
      - pip install PyMuPDF
      - wkhtmltopdf installed on the system
    """
    # Construct the URL for the HTML report
    url = f"https://api.conselldemallorca.net/sit-api/parcelas/{ref_catastral}/informeHTML"
    
    try:
        # Download the HTML content
        with urllib.request.urlopen(url) as response:
            html_content = response.read().decode('utf-8')
        
        # Create a temporary file for the HTML content
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as temp_html:
            temp_html.write(html_content)
            temp_html_path = temp_html.name
        
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
        
        # Convert HTML to PDF using wkhtmltopdf
        subprocess.run([WKHTMLTOPDF_PATH, temp_html_path, temp_pdf_path], check=True)
        
        # Convert PDF to bytes using PyMuPDF
        pdf_document = fitz.open(temp_pdf_path)
        pdf_bytes = pdf_document.tobytes()
        pdf_document.close()
        
        # Clean up temporary files
        os.unlink(temp_html_path)
        os.unlink(temp_pdf_path)
        
        return pdf_bytes
        
    except urllib.error.URLError as e:
        print(f"Error downloading the report: {e}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error converting to PDF: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PTM</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary-color: #1a73e8;
                --primary-hover: #1557b0;
                --background-color: #f8f9fa;
                --card-background: #ffffff;
                --text-color: #202124;
                --border-color: #dadce0;
                --error-color: #d93025;
                --success-color: #188038;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                color: var(--text-color);
                background-color: var(--background-color);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding: 2rem 1rem;
            }

            .container {
                max-width: 600px;
                margin: 0 auto;
                width: 100%;
            }

            .card {
                background-color: var(--card-background);
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 2rem;
            }

            h1 {
                color: var(--text-color);
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1.5rem;
                text-align: center;
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            label {
                display: block;
                margin-bottom: 0.5rem;
                color: var(--text-color);
                font-weight: 500;
                font-size: 0.9rem;
            }

            input[type="text"] {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid var(--border-color);
                border-radius: 4px;
                font-size: 1rem;
                transition: border-color 0.2s;
            }

            input[type="text"]:focus {
                outline: none;
                border-color: var(--primary-color);
            }

            button {
                background-color: var(--primary-color);
                color: white;
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                font-size: 1rem;
                font-weight: 500;
                transition: background-color 0.2s;
            }

            button:hover {
                background-color: var(--primary-hover);
            }

            .error {
                color: var(--error-color);
                margin-top: 1rem;
                text-align: center;
                font-size: 0.9rem;
            }

            .success {
                color: var(--success-color);
                margin-top: 1rem;
                text-align: center;
                font-size: 0.9rem;
            }

            .info {
                margin-top: 1.5rem;
                padding: 1rem;
                background-color: #e8f0fe;
                border-radius: 4px;
                color: var(--primary-color);
                font-size: 0.9rem;
            }

            code {
                background-color: #f1f3f4;
                padding: 0.2rem 0.4rem;
                border-radius: 3px;
                font-family: monospace;
            }

            @media (max-width: 600px) {
                body {
                    padding: 1rem;
                }
                
                .card {
                    padding: 1.5rem;
                }

                h1 {
                    font-size: 1.25rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>PTM</h1>
                <form action="/generate-pdf" method="post">
                    <div class="form-group">
                        <label for="ref_catastral">Referencia Catastral</label>
                        <input type="text" id="ref_catastral" name="ref_catastral" required 
                               placeholder="ej., 07045A00200407" pattern="[0-9A-Z]+">
                    </div>
                    <button type="submit">Generar PDF</button>
                </form>
            </div>

            <div class="info">
                <p>Acceso directo: <code>https://ptm-to-pdf.fly.dev/07045A00200407</code></p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/<ref_catastral>')
def direct_pdf(ref_catastral):
    if not ref_catastral or not ref_catastral.isalnum():
        abort(400, description="Referencia catastral inválida")
    
    print(f"Generating PDF for reference: {ref_catastral}")
    pdf_data = retrieve_informe_as_pdf(ref_catastral)
    
    if pdf_data:
        pdf_io = BytesIO(pdf_data)
        response = Response(pdf_io, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename=informe_{ref_catastral}.pdf'
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    else:
        abort(404, description="Error al generar el PDF")

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    ref_catastral = request.form.get('ref_catastral')
    if not ref_catastral:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                body { 
                    font-family: 'Inter', sans-serif;
                    text-align: center; 
                    padding: 2rem;
                    background-color: #f8f9fa;
                }
                .error { 
                    color: #d93025;
                    margin: 1rem 0;
                }
                a {
                    color: #1a73e8;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="error">Por favor, introduce una referencia catastral.</div>
            <a href="/">Volver</a>
        </body>
        </html>
        ''', 400

    print(f"Generating PDF for reference: {ref_catastral}")
    pdf_data = retrieve_informe_as_pdf(ref_catastral)
    
    if pdf_data:
        pdf_io = BytesIO(pdf_data)
        response = Response(pdf_io, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename=informe_{ref_catastral}.pdf'
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    else:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                body { 
                    font-family: 'Inter', sans-serif;
                    text-align: center; 
                    padding: 2rem;
                    background-color: #f8f9fa;
                }
                .error { 
                    color: #d93025;
                    margin: 1rem 0;
                }
                a {
                    color: #1a73e8;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="error">Error al generar el PDF. Por favor, verifica la referencia catastral e inténtalo de nuevo.</div>
            <a href="/">Volver</a>
        </body>
        </html>
        ''', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
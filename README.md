# PTM to PDF

A Flask web application that generates PDF reports from property reference numbers using the Consell de Mallorca API.

## Features

- Simple web interface for entering property reference numbers
- Direct URL access for PDF generation
- Automatic PDF download
- Deployed on fly.io

## Requirements

- Python 3.9+
- wkhtmltopdf
- Dependencies listed in requirements.txt

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ptm-to-pdf.git
cd ptm-to-pdf
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Install wkhtmltopdf:
   - Linux: `sudo apt-get install wkhtmltopdf`
   - Windows: Download from [wkhtmltopdf downloads](https://wkhtmltopdf.org/downloads.html)

## Usage

1. Run the application locally:
```bash
python src/main.py
```

2. Access the web interface at `http://localhost:8080`

3. Enter a property reference number (e.g., 07045A00200407)

4. The PDF will be generated and downloaded automatically

## Direct URL Access

You can also generate PDFs directly using URLs:
```
https://ptm-to-pdf.fly.dev/07045A00200407
```

## Deployment

The application is deployed on fly.io. To deploy your own instance:

1. Install flyctl
2. Login to fly.io
3. Deploy the application:
```bash
fly launch
fly deploy
```

## License

MIT 
# Handwriting Decoder

An AI-powered system that recognizes and digitizes handwritten text from images. This application allows users to upload images of handwritten notes and converts them into editable digital text while preserving formatting.

## Features

- Image upload for handwritten text
- AI-powered OCR processing
- Text extraction with formatting preservation
- User-friendly interface
- Real-time processing status updates

## Tech Stack

- Backend: Django (Python)
- Frontend: React (JavaScript)
- Database: PostgreSQL
- OCR: Tesseract.js

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Tesseract.js

## Setup Instructions

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Run the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Upload an image containing handwritten text
3. Wait for the processing to complete
4. View and edit the extracted text

## License

MIT License 
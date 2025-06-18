# Internshala Job Search Flask Application

This is a Flask web application that allows users to search for internships on Internshala.com. The application provides a user-friendly interface to search for internships based on position, experience, and city.

## Features

- Search internships by position, experience, and city
- Autocomplete suggestions for positions
- View detailed job information
- Download search results as Excel file
- Modern and responsive UI

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

4. Create the necessary directories:
```bash
mkdir templates downloads
```

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter a position in the search box (autocomplete suggestions will appear)
2. Select a position from the suggestions
3. Enter experience in years (optional)
4. Enter city name (optional)
5. Set maximum pages to search
6. Click "Search Jobs" to start the search
7. View results and download them as Excel if needed

## Notes

- The application uses Playwright for web scraping
- Search results are saved in the `downloads` directory
- The application runs in debug mode by default
- Make sure you have a stable internet connection for searching

## Requirements

- Python 3.8 or higher
- Flask
- Playwright
- Pandas
- Openpyxl

## File Structure

```
├── app.py                 # Flask web application
├── internshala.py        # Core scraping logic
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Features

- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Validation**: Form validation with helpful error messages
- **Loading Indicators**: Shows progress while searching
- **Error Handling**: Graceful error handling with user-friendly messages
- **Excel Export**: Automatic Excel file generation with results
- **Modern UI**: Beautiful gradient design with smooth animations

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Scraping**: BeautifulSoup4, Requests
- **Data Processing**: Pandas
- **File Export**: OpenPyXL for Excel files

## Troubleshooting

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that port 5000 is not in use by another application
- Ensure you have a stable internet connection for web scraping
- If you encounter errors, check the browser console for details 
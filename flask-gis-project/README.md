# Flask GIS Project

This project is a web application built using Flask that provides a platform for displaying and interacting with maps of ancient architecture and cultural relics in Beijing.

## Project Structure

```
flask-gis-project
├── app
│   ├── __init__.py
│   ├── routes.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   ├── templates
│   │   └── main.html
├── app.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd flask-gis-project
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required packages:**
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, execute the following command:

```
python app.py
```

The application will be accessible at `http://127.0.0.1:5000`.

## Usage

- Navigate to the map section to view the interactive map.
- Use the search functionality to find ancient architecture or cultural relics.
- Change the map style using the provided dropdown menu.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
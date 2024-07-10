# Employee Attendance System

This is a Django-based project that manages employee attendance using facial recognition. The system allows employees to register their faces, mark attendance, and allows managers to view various attendance reports.

## Features

- **Facial Recognition**: 
  - Employees can register their faces and mark attendance using facial recognition. 
  - The system ensures that employees who have already registered their faces cannot register again, preventing duplicate registrations. Make sure to calibrate the model when many new faces have been registered.

- **Attendance Reports**: 
  - Managers/Employees can see/download various types of attendance reports:
    - **Daily**: Attendance for the current day.
    - **Weekly**: Attendance for the current week.
    - **Monthly**: Attendance for the current month.
    - **Total**: Attendance for all time.
    - **Custom Date Range**: Attendance for a specific date range chosen by the user.

- **Google Sheets Integration**: 
  - Attendance data is maintained using Google Sheets, allowing for easy access and management.

- **Employee Management**: 
  - Managers can view, approve, and remove employee records.
  - Managers can approve or reject face update requests from employees.

- **Location-Based Login Approval**: 
  - The system includes a feature where managers can approve or reject login attempts from unauthorized or unregistered locations.

- **Face Update Requests**: 
  - Employees can request to update their registered faces, and managers can approve or reject these requests.


## Installation

### Prerequisites

- Python 3.x
- Django
- TensorFlow
- OpenCV
- Google API Client
- Pandas
- Pillow
- MySQL Server

### Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/employee-attendance-system.git
    cd employee-attendance-system
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up MySQL**:
    - Install MySQL Server and create a database.
    - Update your Django `settings.py` file with your MySQL database configuration:
      ```python
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.mysql',
              'NAME': 'your_database_name',
              'USER': 'your_database_user',
              'PASSWORD': 'your_database_password',
              'HOST': 'localhost',
              'PORT': '3306',
          }
      }
      ```

5. **Set up Google Sheets API**:
    - Follow [this guide](https://developers.google.com/sheets/api/quickstart/python) to set up Google Sheets API and obtain `credentials.json`.
    - Place the `credentials.json` file in your project directory.

6. **Run migrations**:
    ```sh
    python manage.py migrate
    ```

7. **Create a superuser**:
    ```sh
    python manage.py createsuperuser
    ```

8. **Run the server**:
    ```sh
    python manage.py runserver
    ```

## Usage

- Access the admin panel at `http://127.0.0.1:8000/admin` to manage employees.
- Employees can register their faces and mark attendance through the web interface.
- Managers can view and download attendance reports.
- Managers can approve or reject login attempts from unauthorized locations.
- Managers can approve or reject face update requests from employees.

## Project Structure

- `app1/`: Main application containing views, models, and utilities and the basic outlook of the website
- `app2_ML/`: Application containing machine learning related code for facial recognition.
- `templates/`: HTML templates for rendering web pages.
- `static/`: Static files (CSS, JS).
- `media/`: The images of the employees and the model is stored here

## Contributing

Contributions are welcome! Please create a pull request or open an issue to discuss your changes.


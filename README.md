# Equity Optimizer App

This project is deployed to Heroku and is available for testing at the following address: [https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/). It comes preloaded with over 400 stock tickers for immediate use.

## About

The Equity Optimizer App is designed to help users analyze and optimize their stock portfolios. The application provides a range of features to track stock performance and evaluate investment strategies.

## Features

- User authentication and profile management
- Add and manage stocks in a portfolio
- View stock details and performance metrics
- Generate detailed reports for analysis
- Responsive design for all devices
- API features for advanced integrations and data access ([API Documentation](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/api/docs))

## Installation

To set up the app locally or for deployment, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Kamend1/equity-optimizer-app.git
   ```

2. Navigate to the project directory:
   ```bash
   cd equity-optimizer-app
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Update `settings.py` for PostgreSQL configuration:
   Replace the default database settings with:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': '<your-db-name>',
           'USER': '<your-db-user>',
           'PASSWORD': '<your-db-password>',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

6. Configure other necessary settings in `settings.py`:
   - Set `DEBUG = True` for local development.
   - Update `ALLOWED_HOSTS`:
     ```python
     ALLOWED_HOSTS = ['localhost', '127.0.0.1']
     ```
   - Configure email backend for notifications (optional):
     ```python
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
     EMAIL_HOST = '<your-email-host>'
     EMAIL_PORT = 587
     EMAIL_USE_TLS = True
     EMAIL_HOST_USER = '<your-email-username>'
     EMAIL_HOST_PASSWORD = '<your-email-password>'
     ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

Visit `http://127.0.0.1:8000/` in your browser to access the application. Sign up for an account, and start adding stocks to your portfolio.

## API Features

The app provides an API for advanced integrations and data access. You can explore the API and its features using the provided documentation:

- [API Documentation](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/api/docs)

The API will continue to be developed to support additional features and enhance user functionality.

## Testing

The app is deployed on Heroku and available for testing at the following link: [https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

For any queries or support, please contact [kamendd@hotmail.com](mailto:kamendd@hotmail.com).

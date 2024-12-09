# Equity Optimizer App

This project is deployed to Heroku and is available for testing at the following address: [Equity Optimizer App on Heroku](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/). It comes preloaded with over 400 stock tickers for immediate use.

---

## About

The **Equity Optimizer App** is designed to help users analyze and optimize their stock portfolios. The application provides a range of features to track stock performance and evaluate investment strategies.

**Note**: Due to the limitations of lower-tier Heroku plans (specifically regarding RAM), simulations should currently be run with no more than **1500 simulation runs** to ensure optimal performance.

---

## Features

- **User Authentication and Profile Management**
- **Portfolio Management**: Add and manage stocks in a portfolio.
- **Stock Details and Metrics**: View detailed stock performance metrics.
- **Simulation Reports**: Generate and analyze reports for investment strategies.
- **Responsive Design**: Accessible on all devices.
- **API Integration**: Includes robust API features for advanced integrations and data access:
  - [Production API Documentation](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/api/docs)
  - [Local API Documentation](http://127.0.0.1:8000/api/docs/)
- **Asynchronous Email Notifications**: A welcome email is sent asynchronously to new users upon registration using Django signals.

---

## Installation

### Step-by-Step Guide

1. **Clone the repository**:
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
- [Local API Documentation](http://127.0.0.1:8000/api/docs/)

The API will continue to be developed to support additional features and enhance user functionality.

## Testing

The app is deployed on Heroku and available for testing at the following link: [https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/).

## Additional Information

### Asynchronous Email Notification:

The accounts app includes a Django signal that triggers an asynchronous welcome email upon user registration. This ensures a smooth onboarding experience for new users.

### Simulation Restrictions:

Simulations on Heroku should be limited to 1500 runs due to RAM constraints on lower-tier plans.

### SoftUni Graders:

For your convenience, the project defense PowerPoint presentation file is included in the repository root directory as project_defense.pptx.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

For any queries or support, please contact [kamendd@hotmail.com](mailto:kamendd@hotmail.com).

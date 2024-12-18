# Equity Optimizer App

This project is deployed to Heroku and is available for testing at the following address: [Equity Optimizer App on Heroku](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/). It comes preloaded with over 400 stock tickers for immediate use.

**Note**: Due to the limitations of lower-tier Heroku plans (specifically regarding RAM), simulations should currently be run with no more than **1500 simulation runs** to ensure optimal performance.
**Note**: YFinance at the moment recognizes the Heroku Deployment as a commercial product and limits daily data, which obstructs stock price updates. Data is updated until including December 10th.


---

## About

The **Equity Optimizer App** is designed to help users analyze and optimize their stock portfolios. The application provides a range of features to track stock performance and evaluate investment strategies.

---

## Features

- **User Authentication and Profile Management**
- **Portfolio Management**: Add and manage stocks in a portfolio via maintaining favorite lists and running simulations.
- **Stock Details and Metrics**: View detailed stock performance metrics.
- **Simulation Reports**: Apply real-live Harry Markowitz efficient frontier simulation via Monte Carlos simulations with up to 50 stocks and up to 20 000 runs. Generate and analyze reports for investment strategies.
- **Responsive Design**: Accessible on all devices.
- **API Integration**: Includes API features for advanced integrations and data access:
  - [Production API Documentation](https://equityoptimizerapp-9972d7f8e60a.herokuapp.com/api/docs)
  - [Local API Documentation](http://127.0.0.1:8000/api/docs/)
- **Asynchronous Email Notifications**: A welcome email is sent asynchronously to new users upon registration using Django signals.

---

## Installation

**The EquityOptimizerApp requires Python 3.12**

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

7. Celery and Redis Configuration

This project uses Celery for asynchronous task management and Redis as the message broker and result backend. Before running the application, ensure that you have Redis installed and running on your system.

### Environment Variables
The following environment variables need to be configured in your .env file:

CELERY_BROKER_URL: Specifies the URL for the Redis message broker.
Default: redis://localhost:6379/0
CELERY_RESULT_BACKEND: Specifies the URL for Redis to store task results.
Default: redis://localhost:6379/0

### Setting Up Redis
Install Redis:

For Linux:
 ```bash
sudo apt update
sudo apt install redis
```

For macOS (using Homebrew):
 ```bash
brew install redis
```

For Windows, download Redis from the official website.

Start Redis:

```bash

redis-server
```

Verify Redis is Running:

```bash
redis-cli ping
```

Expected output: PONG


Starting Celery Worker -> Run the following command to start the Celery worker:

```bash
celery -A EquityOptimizerApp worker --loglevel=info
```

Optional: Starting Celery Beat Scheduler
If you are using Celery Beat for periodic tasks, run:

```bash
celery -A EquityOptimizerApp beat --loglevel=info
 ```

8. Run the development server:
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

**Note**: Due to the limitations of lower-tier Heroku plans (specifically regarding RAM), simulations should currently be run with no more than **1500 simulation runs** to ensure optimal performance.
**Note**: YFinance at the moment recognizes the Heroku Deployment as a commercial product and limits daily data, which obstructs stock price updates. Data is updated until including December 10th.

## Additional Information

### Asynchronous Email Notification:

The accounts app includes a Django signal that triggers an asynchronous welcome email upon user registration. This ensures a smooth onboarding experience for new users.

### Simulation Restrictions:

Simulations on Heroku should be limited to 1500 runs due to RAM constraints on lower-tier plans.

### Historical Data:

The App utilizes the Yfinace for fetching data about stocks. This API is intended only for educational purposes.

The App has an abstract Data Fecther class, which could implemented with a different API provider. The intended API provider for commercial use would **Alpha Vantage**.

### SoftUni Graders:

For your convenience, the project defense PowerPoint presentation file is included in the repository root directory as project_defense.pptx.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

For any queries or support, please contact [kamendd@hotmail.com](mailto:kamendd@hotmail.com).

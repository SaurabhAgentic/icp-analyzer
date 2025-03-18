# ICP Analyzer

A web application for analyzing ICP (Intracranial Pressure) data with advanced visualization and analysis capabilities.

## Features

- Real-time ICP data visualization
- Statistical analysis tools
- User authentication and authorization
- Data export capabilities
- Interactive charts and graphs
- Mobile-responsive design

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for frontend development)
- Optional: MongoDB 4.4 or higher (for persistent storage)
- Optional: Redis 6.2 or higher (for caching and task queue)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/icp_analyzer.git
cd icp_analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development

1. Start the development server:
```bash
flask run
```

2. Run tests:
```bash
pytest
```

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following environment variables:
   - `PYTHON_VERSION`: 3.8
   - `FLASK_ENV`: production
   - `FLASK_APP`: wsgi.py
   - `USE_REDIS`: false (set to true if using Redis)
   - `USE_MONGODB`: false (set to true if using MongoDB)
   - `SECRET_KEY`: Your secret key
   - `JWT_SECRET_KEY`: Your JWT secret key

4. Set the build command:
```bash
pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

5. Set the start command:
```bash
gunicorn wsgi:app
```

## Contributing

Please read [CONTRIBUTING.md](.github/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

Please read [SECURITY.md](.github/SECURITY.md) for details on our security policy and how to report vulnerabilities. 
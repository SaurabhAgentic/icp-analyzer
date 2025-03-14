# ICP Analyzer

An intelligent agent that analyzes company websites to determine their Ideal Customer Profile (ICP).

## Features

- Web scraping of company websites
- Analysis of website content, including:
  - Target audience identification
  - Industry focus
  - Company size targeting
  - Geographic focus
  - Pain points addressed
  - Value propositions
- AI-powered insights generation
- Structured ICP report generation

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=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
     ```

## Usage

```python
from src.analyzer import ICPAnalyzer

analyzer = ICPAnalyzer()
icp_report = analyzer.analyze_website("https://example.com")
print(icp_report)
```

## Project Structure

```
icp_analyzer/
├── src/
│   ├── analyzer.py        # Main analyzer class
│   ├── scraper.py        # Web scraping functionality
│   ├── processor.py      # Text processing and NLP
│   └── report.py         # Report generation
├── tests/                # Unit tests
├── data/                 # Data storage
└── requirements.txt      # Project dependencies
``` 
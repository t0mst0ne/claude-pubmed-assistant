# Claude PubMed Assistant

A simple API service integrating PubMed academic literature search with Claude AI assistant.

## 🌟 Features

- 🔍 Quickly search the PubMed medical literature database
- 📊 Get structured research article data in JSON format
- 📝 Generate formatted output optimized for Claude
- 🌐 Provide a simple web interface for searching
- 🤖 Offer templates for AI prompts
- 🔄 Support advanced search parameters (date ranges, sorting, etc.)

## 🚀 Quick Start

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/claude-pubmed-assistant.git
cd claude-pubmed-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python run.py
```

The server will start at http://localhost:8000 and automatically open in your browser

### Usage

#### Using the Web Interface

1. Open your browser and visit http://localhost:8000
2. Enter search terms and set parameters
3. Click the "Search" button
4. Copy the results to the Claude dialogue box

#### Using the API

```python
import requests
import json

# Basic search
response = requests.post('http://localhost:8000/api/search', 
                        json={'query': 'covid vaccine'})
results = response.json()

# Advanced search
response = requests.post('http://localhost:8000/api/search', 
                        json={
                            'query': 'stroke treatment',
                            'max_results': 15,
                            'sort': 'date',
                            'since_year': 2022
                        })
results = response.json()

# Get Claude-optimized format
response = requests.post('http://localhost:8000/api/claude_format', 
                        json={
                            'query': 'diabetes management',
                            'max_results': 5
                        })
claude_text = response.json()['formatted_text']
print(claude_text)  # Copy to Claude dialogue box
```

## 📖 How It Works

1. The server receives a search request
2. It queries medical literature using the PubMed E-utilities API
3. It parses the results into structured data
4. It returns JSON or formatted Markdown content
5. The user provides the results to Claude for analysis and summarization

## 🧩 Collaborating with Claude

Best practices:

1. First search for relevant literature
2. Use the "Claude Optimized Format" feature
3. Copy the formatted results to the Claude dialogue box
4. Provide clear instructions to Claude, such as:
   - "Please analyze these latest research studies on heart disease treatments"
   - "Summarize the main findings and methodologies of these papers"
   - "Compare the results of these different studies and explain the differences"

See `examples/claude_prompt.md` for more prompt templates.

## 🛠️ Advanced Configuration

The following options can be set in the `.env` file:
```
PUBMED_API_KEY=your_api_key_here  # Optional but recommended
HOST=0.0.0.0                      # Server host
PORT=8000                         # Server port
DEBUG=False                       # Should be False in production
```

## 📋 API Reference

### `POST /api/search`

Parameters:
- `query` (required): Search terms
- `max_results` (optional, default=10): Maximum number of results
- `sort` (optional, default="relevance"): Sort method ("relevance" or "date")
- `since_year` (optional): Only show results after a specific year

Returns: List of articles in JSON format

### `POST /api/claude_format`

Parameters same as above, returns:
- `formatted_text`: Markdown formatted text optimized for Claude

### `GET /api/article/<pmid>`

Parameters:
- `pmid`: PubMed ID

Returns: Detailed information about a specific article

## 📚 Dependencies

This project relies on only three main packages:
- Flask (Web framework)
- httpx (Asynchronous HTTP client)
- python-dotenv (Environment variable management)

## 🔄 Troubleshooting

If you encounter issues:

1. **Dependency errors**: Make sure you've installed all dependencies with `pip install -r requirements.txt`
2. **Connection errors**: Check your network connection and the PubMed API status
3. **Startup failures**: Check if the port is already in use and try modifying the PORT setting in the `.env` file
4. **Empty search results**: Adjust your search terms and try using PubMed's advanced search syntax

## 📜 License

MIT

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📮 Contact

[Your email or contact information]

# FX CLI

A command-line tool for fetching foreign exchange rates using the OpenExchangeRates API.

## Features

- Get current and historical exchange rates
- Convert between any two currencies
- Clean, simple command-line interface
- Support for 'today' keyword for current rates

## Installation

### Quick Install (Recommended)

```bash
# Install pipx if you don't have it
brew install pipx

# Install fx-cli directly from GitHub
pipx install git+https://github.com/mah-codes/fx-cli.git
```

### Alternative: From Source

```bash
git clone https://github.com/mah-codes/fx-cli.git
cd fx-cli
pipx install .
```

### For Development

```bash
git clone https://github.com/mah-codes/fx-cli.git
cd fx-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Setup

1. Get a free API key from [OpenExchangeRates](https://openexchangerates.org/signup)
2. Create a `.env` file in your home directory or project directory:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   FX_API_KEY=your_actual_api_key_here
   ```

## Usage

### Get USD to Currency Rate
```bash
fx today AED
fx 2024-01-15 EUR
```

### Convert Between Currencies
```bash
fx today BRL USD
fx 2024-01-15 EUR GBP
```

### Options
- `--verbose, -v`: Show verbose output
- `--help`: Show help message

## Examples

```bash
# Get current USD to Brazilian Real rate
fx today BRL

# Get historical USD to Euro rate
fx 2024-01-15 EUR

# Convert Brazilian Real to US Dollar today
fx today BRL USD

# Convert Euro to British Pound on specific date
fx 2024-01-15 EUR GBP

# Verbose output
fx today BRL USD --verbose
```

## Requirements

- Python 3.8+
- Valid OpenExchangeRates API key

## License

MIT License

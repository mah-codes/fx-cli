"""API module for fetching foreign exchange rates."""

import requests
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()


class FXAPIError(Exception):
    """Custom exception for FX API errors."""
    pass


class FXAPI:
    """Foreign Exchange API client."""
    
    def __init__(self):
        self.api_key = os.getenv('FX_API_KEY')
        if not self.api_key:
            # Try to load from user's config directory
            self._load_api_key_from_config()
        if not self.api_key:
            self._prompt_for_api_key()
        self.base_url = "https://openexchangerates.org/api"
    
    def _load_api_key_from_config(self):
        """Load API key from user's config directory."""
        config_file = Path.home() / ".config" / "fx-cli" / ".env"
        if config_file.exists():
            # Load the config file and set environment variable
            load_dotenv(config_file)
            self.api_key = os.getenv('FX_API_KEY')
    
    def _prompt_for_api_key(self):
        """Prompt user for API key if not found in environment."""
        print("🔑 FX_API_KEY not found in environment.")
        print("Get your free API key from: https://openexchangerates.org/signup")
        print()
        
        while True:
            api_key = input("Enter your API key (or 'N' to exit): ").strip()
            
            if api_key.upper() == 'N':
                raise FXAPIError("API key required to continue. Exiting.")
            
            if api_key:
                self.api_key = api_key
                # Save API key to .env file for future use
                self._save_api_key_to_env(api_key)
                print("✅ API key set successfully and saved to ~/.config/fx-cli/.env")
                break
            else:
                print("❌ Please enter a valid API key or 'N' to exit.")
    
    def _save_api_key_to_env(self, api_key: str):
        """Save API key to user's home directory config file."""
        # Create config directory in user's home
        config_dir = Path.home() / ".config" / "fx-cli"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Use .env file in config directory
        env_file = config_dir / ".env"
        
        # Read existing .env content
        existing_content = ""
        if env_file.exists():
            existing_content = env_file.read_text()
        
        # Update or add FX_API_KEY
        lines = existing_content.split('\n') if existing_content else []
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('FX_API_KEY='):
                lines[i] = f'FX_API_KEY="{api_key}"'
                updated = True
                break
        
        if not updated:
            lines.append(f'FX_API_KEY="{api_key}"')
        
        # Write back to .env file
        env_file.write_text('\n'.join(lines))
        
        # Set file permissions to be readable only by user (600)
        # Only set permissions on Unix-like systems (Windows doesn't support chmod)
        try:
            env_file.chmod(0o600)
        except (NotImplementedError, OSError):
            # Windows or other systems that don't support chmod
            # On Windows, file permissions are handled differently
            pass
    
    def refresh_api_key(self):
        """Prompt user for a new API key and save it."""
        print("🔄 API key needs to be updated.")
        self._prompt_for_api_key()
    
    def get_historical_rates(self, date: str) -> Dict[str, float]:
        """
        Get historical exchange rates for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary of currency codes to exchange rates
            
        Raises:
            FXAPIError: If API request fails
        """
        url = f"{self.base_url}/historical/{date}.json"
        params = {
            "app_id": self.api_key,
            "show_alternative": False,
            "prettyprint": False
        }
        headers = {"accept": "application/json"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            # Handle authentication errors specifically
            if response.status_code == 401:
                raise FXAPIError(
                    "Invalid or expired API key. Please check your API key and try again. "
                    "Get a free API key from: https://openexchangerates.org/signup"
                )
            elif response.status_code == 403:
                raise FXAPIError(
                    "API access forbidden. Please check your API key permissions. "
                    "Get a free API key from: https://openexchangerates.org/signup"
                )
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                raise FXAPIError(f"API Error: {data.get('message', 'Unknown error')}")
            
            return data.get('rates', {})
            
        except requests.exceptions.RequestException as e:
            raise FXAPIError(f"Network error: {str(e)}")
        except KeyError as e:
            raise FXAPIError(f"Unexpected API response format: {str(e)}")
    
    def get_rate(self, date: str, currency: str) -> float:
        """
        Get exchange rate for a specific currency on a given date.
        
        Args:
            date: Date in YYYY-MM-DD format
            currency: 3-letter currency code (e.g., 'USD', 'BRL')
            
        Returns:
            Exchange rate relative to USD
            
        Raises:
            FXAPIError: If currency not found or API error
        """
        currency = currency.upper()
        rates = self.get_historical_rates(date)
        
        if currency not in rates:
            raise FXAPIError(f"Currency '{currency}' not found in rates for {date}")
        
        return rates[currency]
    
    def convert_currency(self, date: str, from_currency: str, to_currency: str) -> float:
        """
        Convert between two currencies on a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate from source to target currency
            
        Raises:
            FXAPIError: If currencies not found or API error
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        rates = self.get_historical_rates(date)
        
        if from_currency not in rates:
            raise FXAPIError(f"Currency '{from_currency}' not found in rates for {date}")
        if to_currency not in rates:
            raise FXAPIError(f"Currency '{to_currency}' not found in rates for {date}")
        
        # Convert from source currency to USD, then to target currency
        from_rate = rates[from_currency]
        to_rate = rates[to_currency]
        
        return to_rate / from_rate

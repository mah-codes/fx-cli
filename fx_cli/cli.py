"""Command line interface for FX CLI."""

import click
import datetime
from .api import FXAPI, FXAPIError


@click.command()
@click.argument('date', type=str)
@click.argument('currency', type=str)
@click.argument('target_currency', type=str, required=False)
@click.option('--verbose', '-v', is_flag=True, help='Show verbose output')
def main(date: str, currency: str, target_currency: str = None, verbose: bool = False):
    """
    Get foreign exchange rates.
    
    DATE: Date in YYYY-MM-DD format or 'today'
    CURRENCY: 3-letter currency code (e.g., USD, BRL, EUR)
    TARGET_CURRENCY: Optional target currency for conversion
    """
    try:
        # Handle 'today' keyword
        if date.lower() == 'today':
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Validate date format
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise click.BadParameter(f"Invalid date format: {date}. Use YYYY-MM-DD or 'today'")
        
        # Validate currency codes
        if len(currency) != 3:
            raise click.BadParameter(f"Invalid currency code: {currency}. Must be 3 letters")
        
        if target_currency and len(target_currency) != 3:
            raise click.BadParameter(f"Invalid target currency code: {target_currency}. Must be 3 letters")
        
        # Initialize API client
        api = FXAPI()
        
        if verbose:
            click.echo(f"Fetching rates for {date}...")
        
        if target_currency:
            # Convert between two currencies
            rate = api.convert_currency(date, currency, target_currency)
            click.echo(f'FX rate for {date} {currency} to {target_currency}: {rate:,.4f}')
        else:
            # Get rate relative to USD
            rate = api.get_rate(date, currency)
            click.echo(f'FX rate for {date} USD to {currency}: {rate:,.4f}')
            
    except FXAPIError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()
    except click.BadParameter as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()

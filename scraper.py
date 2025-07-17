#!/usr/bin/env python3
"""Watchcount scraper that fetches pages directly."""

import os
import sys
import json
from rich.console import Console
from rich.table import Table

CONFIG_FILE = 'ebay_config.json'
console = Console()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        console.print(f"[red]Config file '{CONFIG_FILE}' not found. Please create it with your eBay API credentials.[/red]")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def main():
    config = load_config()
    console.print("[bold green]eBay Scraper CLI[/bold green]")
    # Placeholder for menu/commands
    console.print("[yellow]Feature coming soon: Search eBay by keyword, best selling, last sold, etc.[/yellow]")

if __name__ == '__main__':
    main()

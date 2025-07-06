#!/usr/bin/env python3
"""Watchcount scraper that fetches pages directly."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from rich.console import Console
from rich.progress import Progress
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

console = Console()


@dataclass
class Listing:
    id: str
    title: str
    url: str
    price: str
    watch_count: str
    image_url: str


class WatchcountFetcher:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_semaphore = asyncio.Semaphore(3)

    async def __aenter__(self) -> "WatchcountFetcher":
        headers = {"User-Agent": "Mozilla/5.0"}
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session:
            await self.session.close()

    @retry(
        retry=retry_if_exception_type(RuntimeError),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
    )
    async def fetch(self, url: str) -> str:
        assert self.session
        if self.mode == "crawl":
            await self.rate_semaphore.acquire()
        try:
            async with self.session.get(url) as resp:
                await self._handle_rate_limit(resp)
                return await resp.text()
        finally:
            if self.mode == "crawl":
                asyncio.get_event_loop().call_later(60, self.rate_semaphore.release)

    async def _handle_rate_limit(self, resp: aiohttp.ClientResponse) -> None:
        if resp.status == 429:
            retry_after = int(resp.headers.get("Retry-After", "60"))
            console.log(f"Rate limited. Sleeping for {retry_after}s")
            await asyncio.sleep(retry_after)
            raise RuntimeError("Rate limited")
        resp.raise_for_status()


def parse_listings(html: str) -> List[Listing]:
    soup = BeautifulSoup(html, "lxml")
    listings: List[Listing] = []
    for row in soup.select(".resultRow"):
        title_tag = row.select_one(".resultTitle a")
        price_tag = row.select_one(".resultPrice")
        watch_tag = row.select_one(".resultWatch")
        img_tag = row.select_one("img")
        if not title_tag or not price_tag or not img_tag:
            continue
        url = title_tag.get("href", "")
        item_id = url.split("/")[-1].split("?")[0]
        listings.append(
            Listing(
                id=item_id,
                title=title_tag.get_text(strip=True),
                url=url,
                price=price_tag.get_text(strip=True),
                watch_count=watch_tag.get_text(strip=True) if watch_tag else "",
                image_url=img_tag.get("src", ""),
            )
        )
    return listings


async def scrape(args: argparse.Namespace) -> List[Listing]:
    listings: Dict[str, Listing] = {}

    if args.sample_dir:
        for i in range(args.pages):
            path = Path(args.sample_dir) / f"page{i+1}.html"
            html = path.read_text(encoding="utf-8")
            for listing in parse_listings(html):
                listings[listing.id] = listing
        return list(listings.values())

    urls = []
    for i in range(args.pages):
        offset = i * 20
        keywords = quote_plus(args.keywords)
        url = (
            f"https://www.watchcount.com/live/{keywords}/-/all?minPrice={args.min_price}"
            f"&offset={offset}&site={args.site}"
        )
        urls.append(url)

    async with WatchcountFetcher(args.mode) as fetcher:
        if args.mode == "batch":
            html_list = await asyncio.gather(*(fetcher.fetch(u) for u in urls))
            for html in html_list:
                for listing in parse_listings(html):
                    listings[listing.id] = listing
        else:
            for url in urls:
                html = await fetcher.fetch(url)
                for listing in parse_listings(html):
                    listings[listing.id] = listing

    return list(listings.values())


def write_output(listings: List[Listing], path: Optional[str]) -> None:
    data = [listing.__dict__ for listing in listings]
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    else:
        console.print_json(json.dumps(data, indent=2))


async def main() -> int:
    parser = argparse.ArgumentParser(description="Watchcount scraper")
    parser.add_argument("--keywords", required=True)
    parser.add_argument("--min-price", type=float, default=15)
    parser.add_argument("--site", default="EBAY_GB")
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--mode", choices=["batch", "crawl"], default="batch")
    parser.add_argument("--output", type=str)
    parser.add_argument("--sample-dir", type=str)
    args = parser.parse_args()

    try:
        with Progress() as progress:
            task = progress.add_task("scraping", total=args.pages)
            listings = await scrape(args)
            progress.update(task, completed=args.pages)
    except (aiohttp.ClientError, RuntimeError) as e:
        console.print(f"Error: {e}", style="red")
        return 1

    write_output(listings, args.output)
    console.print(f"Fetched {len(listings)} listings")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

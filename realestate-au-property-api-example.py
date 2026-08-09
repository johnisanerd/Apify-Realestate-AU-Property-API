"""Realestate.com.au Property API: a quick-start example.

See more at: https://apify.com/johnvc/realestate-au-property-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/realestate-au-property-api/input-schema?fpr=9n7kx3

This script shows how to call the Realestate.com.au Property API on Apify from
Python and read its structured JSON output. The default run looks up sold
property prices for one Australian suburb, which needs no listing URL at all:
you give it "Coomera, QLD, 4209" and it builds the search for you.

Every run here is deliberately tiny. You are charged per listing returned, so
each example caps maxResultsPerSearch at 3.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3

Examples:
  uv run python realestate-au-property-api-example.py
  uv run python realestate-au-property-api-example.py --example sold
  uv run python realestate-au-property-api-example.py --example rent
  uv run python realestate-au-property-api-example.py --example buy
  uv run python realestate-au-property-api-example.py --example url
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/realestate-au-property-api"

# Keep the first runs cheap. You are billed per listing returned, so 3 listings
# per search is enough to see the shape of the data. Raise this once you have
# your own API key and know your budget; the schema allows up to 2000.
MAX_RESULTS = 3


def _print_items(items: list[dict[str, Any]]) -> None:
    """Print a readable summary of the rows the Actor returned.

    Each dataset row carries a `result_type` of either "listing" or "error", so
    a search that came back empty explains itself instead of vanishing.

    Args:
        items: Rows read from the Actor run's default dataset.
    """
    listings = [row for row in items if row.get("result_type") == "listing"]
    errors = [row for row in items if row.get("result_type") == "error"]

    print(f"Returned {len(items)} row(s): {len(listings)} listing(s), {len(errors)} error row(s).\n")

    for row in listings:
        address = row.get("streetAddress") or "(address withheld)"
        location = " ".join(
            part for part in (row.get("suburb"), row.get("state"), row.get("postcode")) if part
        )
        print(f"{address}, {location}")
        print(
            "  type: {type}  beds: {beds}  baths: {baths}  parking: {parking}  land: {land}".format(
                type=row.get("propertyType", "n/a"),
                beds=row.get("bedrooms", "n/a"),
                baths=row.get("bathrooms", "n/a"),
                parking=row.get("parking", "n/a"),
                land=row.get("landSize", "n/a"),
            )
        )

        # Money reads differently per listing type. On rental rows estimatedPrice
        # is the advertised rent as displayed and rentPrice is its numeric form.
        # Elsewhere estimatedPrice is the source's ESTIMATE, never a confirmed
        # sale price. For-sale rows often carry no number at all, because agents
        # advertise "Contact Agent" or "AUCTION" instead of a figure.
        if row.get("rentPrice"):
            asking = row.get("estimatedPrice") or row["rentPrice"]
            print(f"  advertised rent: {asking} ({row.get('rentCurrency', 'AUD')})")
        elif row.get("estimatedPriceValue") is not None:
            print(
                f"  price estimate: {row.get('estimatedPrice')} "
                f"({row['estimatedPriceValue']}, an estimate rather than a confirmed sale price)"
            )
        elif row.get("estimatedPrice"):
            # For-sale rows frequently show text instead of a figure.
            print(f"  price as advertised: {row['estimatedPrice']} (no number published)")
        else:
            print("  price: not published on this listing")
        if row.get("soldDate"):
            print(f"  sold on: {row['soldDate']}  agency: {row.get('lastSoldAgency', 'n/a')}")

        # The individual agent name is often missing while the agency and phone
        # survive, so read whatever the row actually carries.
        agents = row.get("agents") or []
        if agents:
            first = agents[0]
            who = first.get("name") or first.get("agency") or "unnamed agent"
            print(f"  agent: {who} {first.get('phone', '')}".rstrip())
        if row.get("latitude") is not None and row.get("longitude") is not None:
            print(f"  coordinates: {row['latitude']}, {row['longitude']}")
        if row.get("listingUrl"):
            print(f"  listing: {row['listingUrl']}")
        print()

    for row in errors:
        print(f"ERROR row for {row.get('sourceUrl', 'unknown source')}: {row.get('error_message', '')}")


def _run(client: ApifyClient, run_input: dict[str, Any]) -> None:
    """Call the Actor and print what came back.

    Args:
        client: An authenticated Apify client.
        run_input: The Actor input, built from the published input schema.
    """
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if run is None:
        raise SystemExit("The Actor run did not return a result.")

    print(f"Run id: {run.id}  status: {run.status}")
    # apify-client 3.x returns a typed Run object, so read run.default_dataset_id
    # rather than subscripting a dict.
    items = list(client.dataset(run.default_dataset_id).iterate_items())
    _print_items(items)


def run_sold(client: ApifyClient) -> None:
    """Sold property prices for one suburb. No listing URL needed.

    Sold rows carry a confirmed soldDate, the selling agency, and a price
    estimate. Australian sale prices are frequently undisclosed, so treat
    estimatedPrice as an estimate rather than a settled figure.
    """
    run_input: dict[str, Any] = {
        "mode": "search",
        "listingType": "sold",
        "locations": ["Coomera, QLD, 4209"],
        "maxResultsPerSearch": MAX_RESULTS,
    }
    _run(client, run_input)


def run_rent(client: ApifyClient) -> None:
    """Current rental listings for one suburb, with the advertised rent."""
    run_input: dict[str, Any] = {
        "mode": "search",
        "listingType": "rent",
        "locations": ["Coomera, QLD, 4209"],
        "maxResultsPerSearch": MAX_RESULTS,
    }
    _run(client, run_input)


def run_buy(client: ApifyClient) -> None:
    """Properties for sale across two suburbs at once.

    For-sale rows often carry no numeric price, because Australian agents
    routinely advertise "Contact Agent" or "AUCTION" instead of a figure. Beds,
    baths, parking, land size, agents, and coordinates are still there.
    """
    run_input: dict[str, Any] = {
        "mode": "search",
        "listingType": "buy",
        "locations": ["Coomera, QLD, 4209", "Pimpama, QLD, 4209"],
        "maxResultsPerSearch": MAX_RESULTS,
        "limitPages": 1,
        "splitByPropertyType": False,
        "splitByPriceRange": False,
    }
    _run(client, run_input)


def run_url(client: ApifyClient) -> None:
    """Collect specific listing pages you already hold, in URL mode.

    Swap in your own URLs. Listing pages move as stock turns over, so if a URL
    has gone you get an error row explaining it rather than a silent gap.
    """
    run_input: dict[str, Any] = {
        "mode": "url",
        "listingUrls": [
            "https://www.realestate.com.au/property-house-qld-coomera-136778134",
        ],
    }
    _run(client, run_input)


def main() -> None:
    """Dispatch one of the example runs."""
    parser = argparse.ArgumentParser(description="Realestate.com.au Property API examples")
    parser.add_argument(
        "--example",
        default="sold",
        choices=["sold", "rent", "buy", "url"],
        help="Which example to run. Default is sold property prices for one suburb.",
    )
    args = parser.parse_args()

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_API_TOKEN in .env or the environment.")

    client = ApifyClient(token)
    dispatch = {
        "sold": run_sold,
        "rent": run_rent,
        "buy": run_buy,
        "url": run_url,
    }
    dispatch[args.example](client)


if __name__ == "__main__":
    main()

# ListingOS — Amazon Listing Intelligence Agent

ListingOS is an AI-powered Amazon listing intelligence agent built for the Pixii Founding Engineer project.

It helps Amazon sellers understand why a listing may not convert, how visible it may be in AI-generated shopping answers, and what Pixii-style creative assets should be generated next.

## Why I Built This

Amazon sellers do not only need more content. They need to know what is wrong with their listing and what to fix first.

A seller usually wants to know:

- Why is my listing not converting?
- What are competitors communicating better?
- What trust signals are missing?
- Would AI assistants recommend my product?
- What images or A+ content should I create next?

ListingOS turns a product URL or manually pasted listing details into a structured audit, creative brief, and action plan.

## Core Features

- Optional product URL extraction using Jina Reader
- Gemini-powered structured listing extraction
- Product title, description, buyer question, and competitor auto-fill
- Manual input fallback
- Listing score dashboard
- Executive summary
- AI listing intelligence summary
- AEO visibility simulation
- Pixii-style creative asset recommendations
- Final prioritized action plan

## Tools and APIs Used

- Python
- Streamlit
- Gemini API
- Jina Reader API
- python-dotenv
- requests

## How It Works

1. The user enters a product URL or manually pastes listing details.
2. Jina Reader extracts readable page text from the URL.
3. Gemini cleans the extracted text into structured listing fields.
4. ListingOS calculates listing quality, trust, copy, AEO visibility, and creative opportunity scores.
5. Gemini generates listing intelligence and conversion recommendations.
6. The app generates Pixii-style creative briefs.
7. The app produces a final prioritized action plan.

## Why This Is Useful for Pixii

Pixii helps brands create better Amazon creative assets. ListingOS acts like a pre-creative strategy layer.

It tells the seller:

- what is weak in the listing,
- what buyers care about,
- what competitors may do better,
- and what Pixii should generate next.

This makes the output directly actionable for listing images, comparison graphics, trust badges, lifestyle images, and A+ content.

## Setup Instructions

Clone the repository:

```bash
git clone https://github.com/AishwaryaKharade0311/listingos-pixii-project.git
cd listingos-pixii-project
```

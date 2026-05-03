import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def clean_listing_text(text):
    """
    Cleans messy markdown-style extracted listing text into a readable format.
    """

    if not text:
        return ""

    cleaned_lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove common markdown formatting
        line = line.replace("**", "")
        line = line.replace("__", "")

        # Convert markdown bullets into clean bullets
        if line.startswith("* "):
            line = "• " + line[2:].strip()
        elif line.startswith("- "):
            line = "• " + line[2:].strip()

        # Skip noisy lines
        noisy_phrases = [
            "skip to main content",
            "sign in",
            "sign up",
            "privacy policy",
            "cookies",
            "terms",
            "sponsored",
            "back to top",
        ]

        if any(noise in line.lower() for noise in noisy_phrases):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def clean_query_terms(words):
    """
    Removes common stopwords from matched AEO query terms.
    """

    stopwords = {
        "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with",
        "is", "are", "be", "this", "that", "by", "from", "as", "at", "it",
        "best", "looking", "suitable"
    }

    cleaned = []

    for word in words:
        word = word.lower().strip(".,!?;:()[]{}|/")

        if word and word not in stopwords and len(word) > 2:
            cleaned.append(word)

    return list(dict.fromkeys(cleaned))


def generate_fallback_ai_analysis(product_title, product_description, buyer_question, competitors):
    """
    Generates a structured analysis without calling external APIs.
    This keeps the demo working even if API keys are missing or API calls fail.
    """

    text = f"{product_title} {product_description} {buyer_question}".lower()

    missing_trust_signals = []

    if "third-party tested" not in text and "lab tested" not in text:
        missing_trust_signals.append(
            "Third-party testing, lab testing, warranty, or quality proof")

    if "warranty" not in text and "guarantee" not in text:
        missing_trust_signals.append(
            "Warranty, guarantee, or satisfaction promise")

    if "certified" not in text and "quality" not in text:
        missing_trust_signals.append(
            "Certification, quality standard, or product credibility signal")

    if not missing_trust_signals:
        missing_trust_signals.append(
            "More visible trust-building claims near the top of the listing")

    buyer_criteria = [
        "Clear match with the buyer's exact use case",
        "Visible trust signals such as testing, warranty, certifications, ratings, or quality proof",
        "Specific positioning instead of generic product claims",
        "Easy-to-understand features, benefits, compatibility, and use-case information",
        "Comparison clarity against similar alternatives"
    ]

    competitor_advantages = [
        "Competitors may appear more trustworthy if they show proof signals clearly.",
        "Competitors may win if their listing directly matches the buyer's exact use case.",
        "Competitors may convert better if their images explain benefits faster.",
        "Competitors may rank better in AI answers if their copy contains stronger proof points."
    ]

    improved_title = f"{product_title} | Optimized for {buyer_question.title()}"

    improved_bullets = [
        f"Designed for shoppers searching for: {buyer_question}",
        "Clearly explains the product's main benefit and use case within the first few seconds.",
        "Adds visible trust signals such as warranty, certifications, quality proof, testing, ratings, or compatibility details.",
        "Uses comparison content to explain why this product is better than common alternatives.",
        "Adds lifestyle and problem-solution visuals that match the buyer's real intent."
    ]

    aeo_summary = (
        "The listing has a clear product direction, but it needs stronger answer-engine visibility. "
        "To improve AI recommendation potential, the listing should directly include the buyer query language, "
        "stronger trust proof, use-case-specific benefits, and clearer comparison points."
    )

    return {
        "source": "Fallback Analysis",
        "buyer_criteria": buyer_criteria,
        "missing_trust_signals": missing_trust_signals,
        "competitor_advantages": competitor_advantages,
        "improved_title": improved_title,
        "improved_bullets": improved_bullets,
        "aeo_summary": aeo_summary
    }


def generate_gemini_analysis(product_title, product_description, buyer_question, competitors):
    """
    Uses Gemini to generate structured listing intelligence.
    Falls back safely if the API key is missing or the API call fails.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return generate_fallback_ai_analysis(
            product_title,
            product_description,
            buyer_question,
            competitors
        )

    prompt = f"""
You are an Amazon listing growth strategist working for an AI creative platform like Pixii.

Analyze this Amazon listing from the perspective of an e-commerce seller who wants better conversion and better AI-answer visibility.

Product Title:
{product_title}

Product Description / Bullets:
{product_description}

Buyer Question:
{buyer_question}

Competitors:
{competitors if competitors else "No competitors provided"}

Return ONLY valid JSON with these exact keys:
{{
  "buyer_criteria": ["point 1", "point 2", "point 3", "point 4", "point 5"],
  "missing_trust_signals": ["point 1", "point 2", "point 3"],
  "competitor_advantages": ["point 1", "point 2", "point 3", "point 4"],
  "improved_title": "one improved Amazon title",
  "improved_bullets": ["bullet 1", "bullet 2", "bullet 3", "bullet 4", "bullet 5"],
  "aeo_summary": "short paragraph explaining how to improve answer-engine visibility"
}}

Rules:
- Be specific to the product and buyer question.
- Focus on user pain, conversion, trust, and clarity.
- Keep the analysis category-neutral. Do not assume the product is a supplement unless the listing clearly says so.
- Do not mention that you are an AI model.
- Do not include markdown.
- Do not include extra text outside JSON.
"""

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        content = response.text.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        parsed = json.loads(content)
        parsed["source"] = "Gemini Analysis"
        return parsed

    except Exception as e:
        fallback = generate_fallback_ai_analysis(
            product_title,
            product_description,
            buyer_question,
            competitors
        )
        fallback["source"] = f"Fallback Analysis — Gemini error: {str(e)}"
        return fallback


def simulate_aeo_visibility(product_title, product_description, buyer_question, competitors):
    """
    Simulates whether an AI answer engine would likely recommend this product
    for the buyer's natural-language shopping query.
    """

    text = f"{product_title} {product_description}".lower()
    query_words = clean_query_terms(buyer_question.lower().split())

    matched_words = [word for word in query_words if word in text]

    trust_terms = [
        "third-party tested",
        "lab tested",
        "certified",
        "gmp",
        "non-gmo",
        "vegan",
        "clinically tested",
        "made in",
        "warranty",
        "guarantee",
        "authentic",
        "durable",
        "premium",
        "compatible",
        "high quality",
        "customer reviews",
        "rating",
        "brand",
        "material",
        "quality",
        "safe",
        "safety"
    ]

    proof_matches = [term for term in trust_terms if term in text]

    match_score = min(40, len(matched_words) * 10)
    trust_score = min(30, len(proof_matches) * 6)

    clarity_score = 0

    if len(product_description) > 250:
        clarity_score += 10

    if (
        "benefit" in text
        or "supports" in text
        or "features" in text
        or "designed" in text
        or "compatible" in text
    ):
        clarity_score += 10

    if competitors.strip():
        clarity_score += 10

    total_score = min(100, match_score + trust_score + clarity_score)

    if total_score >= 75:
        verdict = "Strong"
        likely_position = "Likely to appear in top recommendations"
    elif total_score >= 45:
        verdict = "Moderate"
        likely_position = "May appear, but competitors with stronger trust signals could outrank it"
    else:
        verdict = "Weak"
        likely_position = "Unlikely to appear unless the listing copy becomes more specific"

    reasons = []

    if len(matched_words) < 2:
        reasons.append(
            "The listing does not use enough meaningful language from the buyer's exact query.")
    else:
        reasons.append(
            "The listing matches several important terms from the buyer's search intent.")

    if not proof_matches:
        reasons.append(
            "The listing lacks visible proof signals such as warranty, certifications, compatibility, quality proof, testing, or strong customer trust markers."
        )
    else:
        reasons.append(
            "The listing includes some trust-building proof signals.")

    improvement_actions = [
        "Add the buyer's exact use-case language naturally into the title and bullets.",
        "Add proof signals such as warranty, certifications, compatibility, testing, quality standards, ratings, or material quality.",
        "Create comparison content explaining why this product is better than common alternatives.",
        "Use lifestyle and problem-solution images that match the buyer's intent.",
        "Add an FAQ section answering the buyer question directly."
    ]

    return {
        "aeo_verdict": verdict,
        "aeo_score": total_score,
        "likely_position": likely_position,
        "matched_query_terms": matched_words,
        "trust_terms_found": proof_matches,
        "reasons": reasons,
        "improvement_actions": improvement_actions
    }


def generate_final_action_plan(scores, ai_analysis, aeo_result):
    """
    Creates a prioritized seller action plan from the listing scores,
    AI analysis, and AEO visibility result.
    """

    action_plan = []

    if scores["Trust Signal Score"] < 50:
        action_plan.append({
            "priority": "Priority 1",
            "action": "Add visible trust proof",
            "why": "The listing has weak trust signals, which can reduce buyer confidence and AI recommendation potential.",
            "how": "Add truthful proof signals such as certifications, testing, warranty, material quality, compatibility, manufacturing standards, customer ratings, or clean-label claims depending on the product category."
        })

    if aeo_result["aeo_score"] < 70:
        action_plan.append({
            "priority": "Priority 2",
            "action": "Rewrite the title and bullets around the buyer query",
            "why": "The product partially matches the buyer intent but is not strongly optimized for the exact question.",
            "how": "Use the buyer's exact question language naturally in the title, bullets, FAQ, and A+ content."
        })

    if scores["Creative Opportunity Score"] > 60:
        action_plan.append({
            "priority": "Priority 3",
            "action": "Create Pixii trust and benefit images",
            "why": "The listing has a high creative opportunity score, meaning visuals can explain trust, use case, and benefits faster than text.",
            "how": "Generate a trust badge image, lifestyle image, problem-solution image, and comparison image."
        })

    action_plan.append({
        "priority": "Priority 4",
        "action": "Add comparison content",
        "why": "Competitors may win if shoppers cannot quickly understand why this product is better.",
        "how": "Create a comparison image or A+ module comparing quality, comfort, compatibility, features, use case, value, and trust signals."
    })

    action_plan.append({
        "priority": "Priority 5",
        "action": "Add a buyer-question FAQ section",
        "why": "Answer engines and shoppers both reward clear, direct answers to specific purchase questions.",
        "how": "Add FAQs that directly answer the buyer question, use-case fit, compatibility, quality concerns, and who the product is best for."
    })

    return action_plan[:5]


def generate_executive_summary(scores, ai_analysis, aeo_result):
    """
    Creates a short business-style summary for the seller.
    """

    overall_score = scores["Overall Listing Score"]
    trust_score = scores["Trust Signal Score"]
    creative_score = scores["Creative Opportunity Score"]
    aeo_score = aeo_result["aeo_score"]

    if overall_score >= 75:
        overall_verdict = "Strong listing foundation"
    elif overall_score >= 50:
        overall_verdict = "Moderate listing with clear improvement opportunities"
    else:
        overall_verdict = "Weak listing that needs urgent optimization"

    if trust_score < 50:
        biggest_weakness = (
            "The listing does not show enough trust proof, such as warranty, testing, certifications, compatibility, ratings, or quality standards."
        )
    elif aeo_score < 60:
        biggest_weakness = (
            "The listing is not strongly optimized for the buyer's natural-language search intent."
        )
    else:
        biggest_weakness = (
            "The listing can improve by making its benefits and differentiation clearer."
        )

    if creative_score > 60:
        biggest_opportunity = (
            "Pixii-style creative assets can quickly improve trust, clarity, and conversion."
        )
    else:
        biggest_opportunity = (
            "The listing can improve through sharper copy, stronger A+ content, and clearer positioning."
        )

    recommended_next_move = (
        "Start by strengthening trust proof, then create a trust badge image, comparison image, and buyer-intent FAQ."
    )

    return {
        "overall_verdict": overall_verdict,
        "biggest_weakness": biggest_weakness,
        "biggest_opportunity": biggest_opportunity,
        "recommended_next_move": recommended_next_move
    }


def extract_structured_listing_fields(raw_text, product_url=""):
    """
    Uses Gemini to clean messy extracted page text into structured listing fields.
    Falls back safely if Gemini fails.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not raw_text:
        return {
            "product_title": "Extracted Product Listing",
            "product_description": "",
            "buyer_question": "",
            "competitors": "",
            "source": "No raw text"
        }

    if not api_key:
        return {
            "product_title": "Extracted Product Listing",
            "product_description": raw_text[:4000],
            "buyer_question": "",
            "competitors": "",
            "source": "Fallback Structured Extraction"
        }

    prompt = f"""
You are cleaning messy product page text for an Amazon/e-commerce listing audit tool.

Your job:
From the raw extracted page text, identify the actual product/listing details and ignore navigation, ads, menus, unrelated links, footer text, repeated URLs, and unrelated recommended products.

Product URL:
{product_url}

Raw Extracted Text:
{raw_text[:8000]}

Return ONLY valid JSON with these exact keys:
{{
  "product_title": "clean product title",
  "product_description": "clean product description with useful details and bullet points",
  "buyer_question": "one likely buyer search question for this product",
  "competitors": "3 to 5 likely competitor or alternative product names, separated by new lines"
}}

Rules:
- Focus only on the main product from the URL.
- If the page is not a product page, still infer the best listing title and description from the available text.
- Do not include markdown.
- Do not include raw URLs unless useful.
- Keep the product description clean and seller-friendly.
- Buyer question should sound like a real shopper query.
- Competitors should be realistic alternatives from the same category.
"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        parsed = json.loads(content)

        parsed["product_title"] = clean_listing_text(
            parsed.get("product_title", "Extracted Product Listing")
        )

        parsed["product_description"] = clean_listing_text(
            parsed.get("product_description", raw_text[:4000])
        )

        parsed["buyer_question"] = parsed.get("buyer_question", "").strip()
        parsed["competitors"] = clean_listing_text(
            parsed.get("competitors", ""))

        parsed["source"] = "Gemini Structured Extraction"
        return parsed

    except Exception:
        return {
            "product_title": "Extracted Product Listing",
            "product_description": clean_listing_text(raw_text[:4000]),
            "buyer_question": "",
            "competitors": "",
            "source": "Fallback Structured Extraction"
        }

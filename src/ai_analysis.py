import streamlit as st
from src.ai_analysis import (
    generate_gemini_analysis,
    simulate_aeo_visibility,
    generate_final_action_plan,
    generate_executive_summary,
    extract_structured_listing_fields,
)
from src.url_extractor import extract_text_from_url

st.set_page_config(
    page_title="ListingOS",
    page_icon="🛒",
    layout="wide",
)

# ---------------- Sample Data ----------------

SAMPLE_TITLE = "Magnesium Glycinate 500mg Capsules for Sleep, Stress & Muscle Relaxation"

SAMPLE_DESCRIPTION = """
Magnesium Glycinate 500mg capsules designed to support restful sleep, stress balance, muscle relaxation, and daily wellness.

Key Benefits:
- Supports better sleep quality and relaxation
- Helps reduce muscle cramps and tension
- Gentle on the stomach
- Made with high-absorption magnesium glycinate
- Suitable for adults

Ingredients:
Magnesium Glycinate, vegetable capsule, rice flour.

Current Listing Notes:
The listing explains the product benefits but does not strongly target seniors, does not mention third-party testing, and has limited trust-building content.
"""

SAMPLE_BUYER_QUESTION = "best magnesium supplement for seniors"

SAMPLE_COMPETITORS = """
Nature Made Magnesium Glycinate
Doctor's Best High Absorption Magnesium
Pure Encapsulations Magnesium Glycinate
Qunol Magnesium Glycinate
"""


def load_sample_data():
    st.session_state.product_title = SAMPLE_TITLE
    st.session_state.product_description = SAMPLE_DESCRIPTION
    st.session_state.buyer_question = SAMPLE_BUYER_QUESTION
    st.session_state.competitors = SAMPLE_COMPETITORS


# ---------------- Scoring Logic ----------------

def calculate_basic_scores(title, description, buyer_question, competitors):
    text = f"{title} {description}".lower()

    trust_keywords = [
        "third-party tested",
        "certified",
        "non-gmo",
        "vegan",
        "clinically tested",
        "lab tested",
        "made in",
        "fda",
        "gmp",
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
        "safety",
    ]

    benefit_keywords = [
        "sleep",
        "stress",
        "muscle",
        "relaxation",
        "energy",
        "immunity",
        "digestion",
        "focus",
        "calm",
        "recovery",
        "performance",
        "comfort",
        "sound",
        "audio",
        "clarity",
        "professional",
        "portable",
        "easy",
        "fast",
        "support",
        "improve",
    ]

    trust_score = min(100, sum(10 for word in trust_keywords if word in text))
    benefit_score = min(
        100, sum(8 for word in benefit_keywords if word in text))

    copy_score = 40

    if len(description) > 300:
        copy_score += 20

    if len(title) > 40:
        copy_score += 15

    if "-" in description or "benefit" in description.lower() or "features" in description.lower():
        copy_score += 15

    if buyer_question and buyer_question.lower().split()[0] in text:
        copy_score += 10

    copy_score = min(100, copy_score)

    competitor_score = 70 if competitors.strip() else 45

    creative_opportunity_score = 100 - int((trust_score + benefit_score) / 2)
    creative_opportunity_score = max(30, creative_opportunity_score)

    overall_score = int(
        (trust_score + benefit_score + copy_score + competitor_score) / 4
    )

    aeo_score = int(
        (benefit_score * 0.5) + (trust_score * 0.3) + (copy_score * 0.2)
    )

    return {
        "Overall Listing Score": overall_score,
        "AEO Visibility Score": aeo_score,
        "Trust Signal Score": trust_score,
        "Copy Quality Score": copy_score,
        "Creative Opportunity Score": creative_opportunity_score,
    }


def generate_pixii_creative_brief(title, description, buyer_question):
    text = f"{title} {description} {buyer_question}".lower()

    if "senior" in text or "seniors" in text:
        target_user = "senior adults"
        lifestyle_scene = "a calm senior adult using the product as part of a daily routine"
    elif "fitness" in text or "muscle" in text or "recovery" in text:
        target_user = "fitness-focused adults"
        lifestyle_scene = "an active person using the product after a workout or during recovery"
    elif "skin" in text or "beauty" in text:
        target_user = "beauty and wellness shoppers"
        lifestyle_scene = "a clean beauty-style scene showing the product in a daily self-care routine"
    elif "earphone" in text or "earbud" in text or "audio" in text or "music" in text or "musician" in text:
        target_user = "music lovers, creators, and audio-focused shoppers"
        lifestyle_scene = "a musician or creator using the product in a clean desk or studio setup"
    else:
        target_user = "category-relevant shoppers"
        lifestyle_scene = "a clean lifestyle scene showing the product in a realistic use case"

    creative_brief = [
        {
            "asset": "Main Image Upgrade",
            "goal": "Improve first-click appeal and clarity.",
            "brief": (
                f"Create a clean white-background product image for {title}. "
                "Make the product clearly readable, improve lighting, and show the key parts confidently."
            ),
        },
        {
            "asset": "Lifestyle Image",
            "goal": "Help the buyer imagine using the product.",
            "brief": (
                f"Show {lifestyle_scene}. "
                "The image should feel natural, trustworthy, premium, and relevant to the buyer's use case."
            ),
        },
        {
            "asset": "Trust Badge Image",
            "goal": "Reduce buyer hesitation.",
            "brief": (
                "Create an infographic-style image highlighting truthful trust signals such as quality, compatibility, "
                "warranty, material strength, certifications, testing, customer ratings, or brand credibility depending on the product."
            ),
        },
        {
            "asset": "Comparison Image",
            "goal": "Explain why this product is better than alternatives.",
            "brief": (
                "Create a comparison image showing how this product compares with common alternatives on quality, "
                "use-case fit, comfort, performance, durability, value, and buyer-relevant features."
            ),
        },
        {
            "asset": "Problem-Solution Image",
            "goal": "Connect the product to the buyer's real problem.",
            "brief": (
                f"Create a problem-solution image for the query: '{buyer_question}'. "
                "Show the buyer pain point on one side and the product benefit on the other."
            ),
        },
        {
            "asset": "A+ Content Module",
            "goal": "Improve conversion with deeper education.",
            "brief": (
                "Create an A+ content section explaining who this product is for, how it works, "
                f"when to use it, and why it is suitable for {target_user}."
            ),
        },
    ]

    return creative_brief


# ---------------- Sidebar ----------------

with st.sidebar:
    st.title("ListingOS")
    st.write("Amazon listing intelligence for sellers and growth teams.")

    st.divider()

    st.write("Use this tool to:")
    st.write("• Audit listing quality")
    st.write("• Check AI-answer visibility")
    st.write("• Find missing trust signals")
    st.write("• Generate Pixii-style creative briefs")

    st.divider()

    st.button("Load Sample Demo", on_click=load_sample_data)

    st.caption("Built for the Pixii Founding Engineer project.")


# ---------------- Main Page ----------------

st.title("ListingOS — Amazon Listing Intelligence Agent")
st.caption(
    "Audit Amazon listings, check AI visibility, and generate Pixii-style creative briefs."
)

st.info(
    "Works for any Amazon product — paste a product URL or manually enter title, bullets, buyer question, and competitors."
)

st.divider()

st.subheader("Enter Listing Details")

product_url = st.text_input(
    "Optional Product URL",
    placeholder="Paste an Amazon, Shopify, or product listing URL. The app will try to extract page text using Jina Reader.",
)

extract_button = st.button("Extract Listing Text from URL")

if extract_button:
    if not product_url:
        st.error("Please paste a product URL first.")
    else:
        with st.spinner("Extracting readable listing text with Jina Reader..."):
            extraction_result = extract_text_from_url(product_url)

        if extraction_result["success"]:
            st.success(
                "Raw listing text extracted successfully using Jina Reader.")

            raw_extracted_text = extraction_result["text"]

            with st.spinner("Cleaning and structuring listing details with Gemini..."):
                structured_fields = extract_structured_listing_fields(
                    raw_extracted_text,
                    product_url,
                )

            st.session_state.product_title = structured_fields.get(
                "product_title",
                "Extracted Product Listing",
            )

            st.session_state.product_description = structured_fields.get(
                "product_description",
                raw_extracted_text,
            )

            suggested_buyer_question = structured_fields.get(
                "buyer_question", "")
            suggested_competitors = structured_fields.get("competitors", "")

            if suggested_buyer_question:
                st.session_state.buyer_question = suggested_buyer_question

            if suggested_competitors:
                st.session_state.competitors = suggested_competitors

            if structured_fields.get("source") == "Gemini Structured Extraction":
                st.success(
                    "Listing fields structured successfully with Gemini.")
            else:
                st.warning(
                    "Raw listing text extracted. Please review or edit the fields before running the audit."
                )

            st.caption(
                f"Extraction source: Jina Reader + {structured_fields.get('source', 'Gemini')}. "
                "You can edit the extracted fields before running the audit."
            )

        else:
            st.warning(
                "URL extraction did not work confidently. Please paste the listing details manually."
            )
            st.caption(
                f"Extraction source: {extraction_result['source']}. "
                f"Error: {extraction_result['error']}"
            )

product_title = st.text_input(
    "Product Title",
    key="product_title",
    placeholder="Example: Magnesium Glycinate 500mg for Sleep, Stress & Muscle Relaxation",
)

product_description = st.text_area(
    "Product Description / Bullet Points",
    key="product_description",
    placeholder="Paste the product description, bullets, benefits, ingredients, certifications, etc.",
    height=320,
)

buyer_question = st.text_input(
    "Buyer Question",
    key="buyer_question",
    placeholder="Example: best wired IEM earphones for musicians",
)

competitors = st.text_area(
    "Competitors / Similar Products Optional",
    key="competitors",
    placeholder="Paste competitor names, titles, or URLs if available.",
    height=100,
)

analyze_button = st.button("Run Listing Audit")


# ---------------- Report Generation ----------------

if analyze_button:
    missing_fields = []

    if not product_title:
        missing_fields.append("Product Title")

    if not product_description:
        missing_fields.append("Product Description")

    if not buyer_question:
        missing_fields.append("Buyer Question")

    if missing_fields:
        st.error(f"Please fill: {', '.join(missing_fields)}.")

    else:
        scores = calculate_basic_scores(
            product_title,
            product_description,
            buyer_question,
            competitors,
        )

        st.success("Listing audit generated successfully.")

        st.subheader("ListingOS Report Dashboard")

        score_col1, score_col2, score_col3, score_col4, score_col5 = st.columns(
            5)

        with score_col1:
            st.metric("Overall", f"{scores['Overall Listing Score']}/100")

        with score_col2:
            st.metric("AEO Visibility",
                      f"{scores['AEO Visibility Score']}/100")

        with score_col3:
            st.metric("Trust Signals", f"{scores['Trust Signal Score']}/100")

        with score_col4:
            st.metric("Copy Quality", f"{scores['Copy Quality Score']}/100")

        with score_col5:
            st.metric(
                "Creative Opportunity",
                f"{scores['Creative Opportunity Score']}/100",
            )

        st.caption(
            "Higher Creative Opportunity means the listing has more room for Pixii-style image, copy, and A+ content improvements."
        )

        ai_analysis = generate_gemini_analysis(
            product_title,
            product_description,
            buyer_question,
            competitors,
        )

        aeo_result = simulate_aeo_visibility(
            product_title,
            product_description,
            buyer_question,
            competitors,
        )

        executive_summary = generate_executive_summary(
            scores,
            ai_analysis,
            aeo_result,
        )

        st.divider()

        st.subheader("Executive Summary")

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:
            st.info(
                f"**Overall Verdict:** {executive_summary['overall_verdict']}")
            st.warning(
                f"**Biggest Weakness:** {executive_summary['biggest_weakness']}")

        with summary_col2:
            st.success(
                f"**Biggest Opportunity:** {executive_summary['biggest_opportunity']}")
            st.info(
                f"**Recommended Next Move:** {executive_summary['recommended_next_move']}")

        st.divider()

        st.subheader("Input Summary")

        input_col1, input_col2 = st.columns(2)

        with input_col1:
            st.write("**Product Title:**")
            st.write(product_title)

            st.write("**Buyer Question:**")
            st.write(buyer_question)

        with input_col2:
            st.write("**Competitors:**")
            st.write(competitors if competitors else "No competitors provided.")

        st.write("**Product Details:**")
        st.write(product_description)

        st.divider()

        st.subheader("What Pixii Should Generate Next")

        creative_brief = generate_pixii_creative_brief(
            product_title,
            product_description,
            buyer_question,
        )

        for item in creative_brief:
            with st.expander(item["asset"], expanded=True):
                st.write(f"**Goal:** {item['goal']}")
                st.write(f"**Creative Brief:** {item['brief']}")

        st.divider()

        st.subheader("AI Listing Intelligence Summary")
        st.caption(
            f"Analysis source: {ai_analysis.get('source', 'ListingOS')}")

        with st.expander("Buyer Purchase Criteria", expanded=True):
            for point in ai_analysis["buyer_criteria"]:
                st.write(f"• {point}")

        with st.expander("Missing Trust Signals", expanded=True):
            for point in ai_analysis["missing_trust_signals"]:
                st.write(f"• {point}")

        with st.expander("Why Competitors May Win", expanded=True):
            for point in ai_analysis["competitor_advantages"]:
                st.write(f"• {point}")

        with st.expander("Improved Product Title", expanded=True):
            st.write(ai_analysis["improved_title"])

        with st.expander("Improved Bullet Points", expanded=True):
            for point in ai_analysis["improved_bullets"]:
                st.write(f"• {point}")

        with st.expander("AEO Recommendation Summary", expanded=True):
            st.write(ai_analysis["aeo_summary"])

        st.divider()

        st.subheader("AEO Visibility Simulation")

        aeo_col1, aeo_col2 = st.columns(2)

        with aeo_col1:
            st.metric("AEO Verdict", aeo_result["aeo_verdict"])

        with aeo_col2:
            st.metric("AEO Score", f"{aeo_result['aeo_score']}/100")

        st.info(f"Likely AI Position: {aeo_result['likely_position']}")

        with st.expander("Matched Query Terms", expanded=True):
            if aeo_result["matched_query_terms"]:
                st.write(", ".join(aeo_result["matched_query_terms"]))
            else:
                st.write("No strong query-term match found.")

        with st.expander("Trust Terms Found", expanded=True):
            if aeo_result["trust_terms_found"]:
                st.write(", ".join(aeo_result["trust_terms_found"]))
            else:
                st.write("No major trust terms found.")

        with st.expander("Why This Verdict", expanded=True):
            for reason in aeo_result["reasons"]:
                st.write(f"• {reason}")

        with st.expander("How to Improve AI Recommendation Chances", expanded=True):
            for action in aeo_result["improvement_actions"]:
                st.write(f"• {action}")

        st.divider()

        st.subheader("Final Prioritized Action Plan")

        final_actions = generate_final_action_plan(
            scores,
            ai_analysis,
            aeo_result,
        )

        for item in final_actions:
            with st.container(border=True):
                st.markdown(f"### {item['priority']}: {item['action']}")
                st.write(f"**Why it matters:** {item['why']}")
                st.write(f"**How to execute:** {item['how']}")

import requests


def extract_text_from_url(url):
    """
    Uses Jina Reader API to convert a product/listing URL into clean readable text.
    If extraction fails, it returns a safe error message.
    """

    if not url:
        return {
            "success": False,
            "source": "No URL provided",
            "text": "",
            "error": "No URL was provided."
        }

    cleaned_url = url.strip()

    if not cleaned_url.startswith("http://") and not cleaned_url.startswith("https://"):
        cleaned_url = "https://" + cleaned_url

    jina_url = f"https://r.jina.ai/{cleaned_url}"

    try:
        response = requests.get(jina_url, timeout=20)

        if response.status_code != 200:
            return {
                "success": False,
                "source": "Jina Reader",
                "text": "",
                "error": f"Jina returned status code {response.status_code}."
            }

        extracted_text = response.text.strip()

        if len(extracted_text) < 100:
            return {
                "success": False,
                "source": "Jina Reader",
                "text": extracted_text,
                "error": "Extracted text was too short to use confidently."
            }

        return {
            "success": True,
            "source": "Jina Reader",
            "text": extracted_text[:6000],
            "error": ""
        }

    except Exception as e:
        return {
            "success": False,
            "source": "Jina Reader",
            "text": "",
            "error": str(e)
        }

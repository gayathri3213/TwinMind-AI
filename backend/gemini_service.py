import json
from urllib import response
from google import genai
from google.genai import types


client = genai.Client()


def predict_scenario(product_id, product_name, query):

    prompt = f"""
You are an AI supply-chain scenario analysis system
for a warehouse digital twin.

Product:
Product ID: {product_id}
Product Name: {product_name}

User Scenario:
{query}

Analyze how this scenario could affect the supply of this
product.

Return ONLY valid JSON in exactly this format:

{{
    "impact_percentage": 33,
    "direction": "downward"
}}

Rules:

1. impact_percentage must be a number between 0 and 100.
2. direction must be exactly one of:
   "upward"
   "downward"

3. "upward" means the scenario is expected to increase
   product supply.

4. "downward" means the scenario is expected to decrease
   product supply.

5. Estimate the magnitude based on the scenario and the
   relationship between the event and the product.

6. Do not include explanations or markdown.
7. Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )

    result = json.loads(response.text)

    return result

def explain_scenario(
    product_id,
    product_name,
    query,
    impact_percentage,
    direction
):
    prompt = f"""
Product: {product_name}
Scenario: {query}
Impact: {impact_percentage}%
Direction: {direction}

Write exactly 2 very short sentences.
Sentence 1: Explain why the scenario affects the product.
Sentence 2: Explain the estimated impact and direction.

Maximum 35 words total.
Return only the two sentences.
"""

    response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="low"
        ),
        #max_output_tokens=300
    )
)

    print("GEMINI EXPLANATION:", response.text)
    print("LENGTH:", len(response.text))
    print("FINISH REASON:", response.candidates[0].finish_reason)

    return response.text.strip()
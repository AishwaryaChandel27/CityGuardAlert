import json
import logging
import os

from google import genai
from google.genai import types
from pydantic import BaseModel

# IMPORTANT: KEEP THIS COMMENT
# Follow these instructions when using this blueprint:
# - Note that the newest Gemini model series is "gemini-2.5-flash" or gemini-2.5-pro"
#   - do not change this unless explicitly requested by the user
# - Sometimes the google genai SDK has occasional type errors. You might need to run to validate, at time.  
# The SDK was recently renamed from google-generativeai to google-genai. This file reflects the new name and the new APIs.

# This API key is from Gemini Developer API Key, not vertex AI API Key
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

class IncidentAnalysis(BaseModel):
    relevance_score: float
    severity: str
    category: str
    is_credible: bool
    summary: str

def analyze_incident(title: str, description: str, source: str, location: str) -> IncidentAnalysis:
    """Analyze an incident for relevance, severity, and credibility using Gemini AI"""
    try:
        system_prompt = (
            "You are an expert incident analyst for a local alert system. "
            "Analyze the following incident and provide a structured assessment. "
            "Relevance score should be 0.0-1.0 (1.0 = highly relevant to local safety). "
            "Severity should be: low, medium, high, or critical. "
            "Category should be one of: weather, traffic, crime, emergency, infrastructure, health, other. "
            "Is_credible should assess if this is from a reliable source and not misinformation. "
            "Summary should be a concise 1-2 sentence summary suitable for alerts. "
            "Consider local impact and immediate relevance to residents."
        )
        
        incident_text = f"Title: {title}\nDescription: {description}\nSource: {source}\nLocation: {location}"
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Content(role="user", parts=[types.Part(text=incident_text)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=IncidentAnalysis,
            ),
        )

        raw_json = response.text
        logging.debug(f"Gemini analysis response: {raw_json}")

        if raw_json:
            data = json.loads(raw_json)
            return IncidentAnalysis(**data)
        else:
            raise ValueError("Empty response from Gemini model")

    except Exception as e:
        logging.error(f"Failed to analyze incident with Gemini: {e}")
        # Return default analysis if AI fails
        return IncidentAnalysis(
            relevance_score=0.5,
            severity="medium",
            category="other",
            is_credible=True,
            summary=f"{title}: {description[:100]}..."
        )

def summarize_multiple_incidents(incidents: list) -> str:
    """Generate a summary of multiple incidents for dashboard display"""
    try:
        if not incidents:
            return "No active incidents in your area."
        
        incidents_text = "\n".join([
            f"- {inc.get('title', '')}: {inc.get('ai_summary', inc.get('description', ''))[:100]}"
            for inc in incidents[:10]  # Limit to top 10 incidents
        ])
        
        prompt = (
            "Create a brief, clear summary of these local incidents for a safety dashboard. "
            "Focus on the most important information residents need to know. "
            "Use bullet points and keep it under 200 words:\n\n" + incidents_text
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text or "Multiple incidents reported. Check individual alerts for details."

    except Exception as e:
        logging.error(f"Failed to summarize incidents: {e}")
        return f"Found {len(incidents)} active incidents. Check individual alerts for details."

def filter_credible_sources(content: str, source_url: str = "") -> bool:
    """Use Gemini to assess if content comes from a credible source"""
    try:
        prompt = (
            "Assess if this content appears to be from a credible news or weather source. "
            "Consider: official sources, known news outlets, weather services, government agencies. "
            "Return only 'true' or 'false'.\n\n"
            f"Content: {content[:500]}\n"
            f"Source URL: {source_url}"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        result = response.text.strip().lower() if response.text else ""
        return result == "true"

    except Exception as e:
        logging.error(f"Failed to assess source credibility: {e}")
        return True  # Default to allowing content if AI fails

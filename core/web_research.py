"""
Echoes.exe — External Research Engine via SerpApi
Searches official documentation, migration guides, and CVE security advisories for detected legacy dependencies.
Strictly distinguishes external web claims from repository evidence.
"""
from typing import List, Dict, Any
import requests

from config.settings import settings


class WebResearchEngine:
    SERPAPI_ENDPOINT = "https://serpapi.com/search.json"

    @classmethod
    def search_dependency_advisories(cls, package_name: str, ecosystem: str = "python") -> Dict[str, Any]:
        """
        Queries SerpApi for security advisories, deprecation notices, or migration guides.
        Gracefully returns an unconfigured status if SERPAPI_API_KEY is omitted.
        """
        api_key = settings.SERPAPI_API_KEY.strip()
        if not api_key:
            return {
                "available": False,
                "reason": "SerpApi key not configured. External advisory search disabled.",
                "query": package_name,
                "results": []
            }

        query = f"{package_name} {ecosystem} migration guide OR security advisory OR deprecated"
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": 4
        }

        try:
            resp = requests.get(cls.SERPAPI_ENDPOINT, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                organic = data.get("organic_results", [])
                results = [
                    {
                        "title": r.get("title"),
                        "link": r.get("link"),
                        "snippet": r.get("snippet"),
                        "source": r.get("source") or "Google Search via SerpApi",
                        "disclaimer": "External web result. Not verified repository source evidence."
                    }
                    for r in organic[:4]
                ]
                return {
                    "available": True,
                    "query": query,
                    "results": results
                }
            else:
                return {
                    "available": False,
                    "reason": f"SerpApi returned HTTP {resp.status_code}",
                    "query": query,
                    "results": []
                }
        except requests.RequestException as e:
            return {
                "available": False,
                "reason": f"External research network error: {str(e)}",
                "query": query,
                "results": []
            }

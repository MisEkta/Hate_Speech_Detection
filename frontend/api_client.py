import requests

def check_api_health(api_base_url):
    """Check if the API is running and healthy."""
    try:
        response = requests.get(f"{api_base_url}/health")
        return response.status_code == 200
    except Exception:
        return False

def analyze_text_api(api_base_url, text, include_policies, include_reasoning):
    """Send text to the API for analysis."""
    try:
        payload = {
            "text": text,
            "include_policies": include_policies,
            "include_reasoning": include_reasoning
        }
        response = requests.post(f"{api_base_url}/analyze", json=payload)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection Error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected Error: {str(e)}"}

def analyze_audio_api(api_base_url, audio_bytes, include_policies, include_reasoning):
    """Send audio file to the API for analysis."""
    try:
        files = {"file": audio_bytes}
        params = {
            "include_policies": str(include_policies).lower(),
            "include_reasoning": str(include_reasoning).lower()
        }
        response = requests.post(f"{api_base_url}/analyze_audio", files=files, params=params)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection Error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected Error: {str(e)}"}
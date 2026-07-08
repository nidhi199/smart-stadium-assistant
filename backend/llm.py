import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv()

def get_clients():
    """Returns a tuple of (nim_client, gemini_client)"""
    nim_key = os.getenv("NVIDIA_NIM_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    nim_client = None
    if nim_key and nim_key != "your_nvidia_nim_api_key_here" and OpenAI:
        nim_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=nim_key
        )
        
    gemini_client = None
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        gemini_client = genai.Client(api_key=gemini_key)
        
    return nim_client, gemini_client

def chat_with_fan(user_message, kb_context):
    nim_client, gemini_client = get_clients()
    
    system_prompt = f"""You are the Smart Stadium Assistant for the FIFA World Cup 2026.
You help fans with navigation, amenities, and transport. 
IMPORTANT INSTRUCTIONS:
1. Auto-detect the language of the user's message (English, Spanish, or Hindi) and respond in that SAME language.
2. Be helpful, concise, and friendly.
3. Ground your answers using ONLY the provided knowledge base context. If the answer is not in the context, politely say you don't know but offer general assistance.

KNOWLEDGE BASE CONTEXT:
{kb_context}
"""

    if nim_client:
        try:
            completion = nim_client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling NVIDIA NIM: {e}")
            return f"Sorry, I am currently experiencing technical difficulties with NIM. Error: {str(e)}"
            
    elif gemini_client:
        try:
            response = gemini_client.models.generate_content(
                model='gemini-2.5-pro',
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return "Sorry, I am currently experiencing technical difficulties."
            
    else:
        # Mock response
        return "[Mock Response] The restrooms are near Section 112. (Please configure NVIDIA_NIM_API_KEY or GEMINI_API_KEY to use the real AI)."

def generate_insight(data):
    # Check thresholds
    alerts = []
    
    # Check zones
    for zone in data.get('zones', []):
        capacity_ratio = zone['current_capacity'] / zone['max_capacity']
        if capacity_ratio > 0.90:
            alerts.append(f"Zone {zone['zone_name']} is at {int(capacity_ratio*100)}% capacity.")
            
    # Check incidents
    for incident in data.get('incidents', []):
        if incident['severity'] in ['High', 'Critical']:
            alerts.append(f"High severity incident in {incident['zone_name']}: {incident['description']}.")

    # Check gate flow
    for gate in data.get('gate_flow', []):
        if gate['entry_rate_per_min'] > 100:
            alerts.append(f"Gate {gate['gate_name']} is experiencing high entry flow ({gate['entry_rate_per_min']} per min).")

    if not alerts:
        return "All zones operating normally. No active high-severity alerts."

    alert_text = "\n".join(alerts)
    nim_client, gemini_client = get_clients()
    
    prompt = f"""You are a Stadium Operations AI. Based on the following raw alerts triggered by our rule-based system, write a single concise, professional sentence summarizing the situation and recommending a brief action to the operations staff.
    
    Raw alerts:
    {alert_text}
    """

    if nim_client:
        try:
            completion = nim_client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling NVIDIA NIM: {e}")
            return f"Action required: {alerts[0]}"
            
    elif gemini_client:
        try:
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2)
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return f"Action required: {alerts[0]}"
            
    else:
        # Mock insight
        return f"[Mock Insight] ALERT: {alerts[0]} - recommend rerouting fans or dispatching staff."

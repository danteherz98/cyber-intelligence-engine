import google.generativeai as genai

# PEGA TU API KEY AQUÍ
API_KEY = "AIzaSyCy9KMJRWQgFVXf1zfTrOj3XrtqRjHaF5Q"

genai.configure(api_key=API_KEY)

print("Consultando modelos disponibles...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error conectando a Google: {e}")
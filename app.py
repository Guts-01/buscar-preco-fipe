from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

API_BASE_URL = "https://parallelum.com.br/fipe/api/v1"

@app.route("/", methods=["GET", "POST"])
def index():
    vehicle_type = request.form.get("vehicle_type") or ""
    brands, models, years, vehicle_data = [], [], [], None
    selected_brand = request.form.get("brand") or ""
    selected_model = request.form.get("model") or ""
    selected_year = request.form.get("year") or ""
    error_message = None  

    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

    try:
        if vehicle_type:
            brands = requests.get(f"{API_BASE_URL}/{vehicle_type}/marcas", headers=headers).json()

        if vehicle_type and selected_brand:
            response = requests.get(f"{API_BASE_URL}/{vehicle_type}/marcas/{selected_brand}/modelos", headers=headers).json()
            models = response.get("modelos", [])

        if vehicle_type and selected_brand and selected_model:
            years = requests.get(f"{API_BASE_URL}/{vehicle_type}/marcas/{selected_brand}/modelos/{selected_model}/anos", headers=headers).json()

        if vehicle_type and selected_brand and selected_model and selected_year:
            vehicle_data = requests.get(f"{API_BASE_URL}/{vehicle_type}/marcas/{selected_brand}/modelos/{selected_model}/anos/{selected_year}", headers=headers).json()

        print(f"vehicle_type: {vehicle_type}, selected_brand: {selected_brand}, selected_model: {selected_model}, selected_year: {selected_year}")
        
    except requests.exceptions.RequestException as e:
        error_message = f"Erro ao buscar dados: {e}"

    return render_template("index.html", vehicle_type=vehicle_type, brands=brands, models=models, years=years, vehicle_data=vehicle_data, selected_brand=selected_brand, selected_model=selected_model, selected_year=selected_year, error_message=error_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
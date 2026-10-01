import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

API_BASE_URL = "https://parallelum.com.br/fipe/api/v1"
API_TIMEOUT = 10
VEHICLE_TYPES = {
    "carros": "Carro",
    "motos": "Moto",
    "caminhoes": "Caminhão",
}


class FipeApiError(Exception):
    """Raised when the FIPE API returns an unusable response."""


def fetch_fipe(*path_parts):
    path = "/".join(quote(str(part), safe="") for part in path_parts)
    headers = {}
    if api_key := os.getenv("API_KEY"):
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.get(
        f"{API_BASE_URL}/{path}", headers=headers, timeout=API_TIMEOUT
    )
    response.raise_for_status()

    try:
        return response.json()
    except ValueError as exc:
        raise FipeApiError("Resposta inválida da API FIPE.") from exc


def fetch_options(*path_parts, key=None):
    data = fetch_fipe(*path_parts)
    options = data.get(key) if key and isinstance(data, dict) else data
    if not isinstance(options, list) or any(
        not isinstance(item, dict) or "codigo" not in item or "nome" not in item
        for item in options
    ):
        raise FipeApiError("Lista de opções inválida da API FIPE.")
    return options


def find_option(options, code):
    return next(
        (item for item in options if str(item["codigo"]) == code), None
    )


@app.get("/")
def index():
    vehicle_type = request.args.get("vehicle_type", "").strip()
    selected_brand = request.args.get("brand", "").strip()
    selected_model = request.args.get("model", "").strip()
    selected_year = request.args.get("year", "").strip()

    brands, models, years = [], [], []
    brand, model = None, None
    vehicle_data = None
    error_message = None

    try:
        if vehicle_type and vehicle_type not in VEHICLE_TYPES:
            vehicle_type = ""
            error_message = "Tipo de veículo inválido. Selecione uma opção da lista."
        elif vehicle_type:
            brands = fetch_options(vehicle_type, "marcas")

            if selected_brand:
                brand = find_option(brands, selected_brand)
                if brand is None:
                    selected_brand = selected_model = selected_year = ""
                    error_message = "Marca inválida. Selecione uma opção da lista."
                else:
                    models = fetch_options(
                        vehicle_type, "marcas", selected_brand, "modelos", key="modelos"
                    )

                    if selected_model:
                        model = find_option(models, selected_model)
                        if model is None:
                            selected_model = selected_year = ""
                            error_message = "Modelo inválido. Selecione uma opção da lista."
                        else:
                            years = fetch_options(
                                vehicle_type, "marcas", selected_brand,
                                "modelos", selected_model, "anos",
                            )

                            if selected_year:
                                if find_option(years, selected_year) is None:
                                    selected_year = ""
                                    error_message = "Ano inválido. Selecione uma opção da lista."
                                else:
                                    vehicle_data = fetch_fipe(
                                        vehicle_type, "marcas", selected_brand,
                                        "modelos", selected_model, "anos", selected_year,
                                    )
                                    if not isinstance(vehicle_data, dict) or not vehicle_data.get("Valor"):
                                        raise FipeApiError("Dados do veículo inválidos da API FIPE.")
    except (requests.RequestException, FipeApiError):
        app.logger.exception("Falha ao consultar a API FIPE")
        error_message = "Não foi possível consultar a Tabela FIPE agora. Tente novamente em instantes."

    return render_template(
        "index.html",
        vehicle_types=VEHICLE_TYPES,
        vehicle_type=vehicle_type,
        brands=brands,
        models=models,
        years=years,
        selected_brand=selected_brand,
        selected_model=selected_model,
        selected_year=selected_year,
        brand=brand,
        model=model,
        vehicle_data=vehicle_data,
        error_message=error_message,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

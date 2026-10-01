import unittest
from unittest.mock import Mock, patch

import requests

from app import app


class FipePageTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.requests.get")
    def test_full_consultation_and_progressive_fields(self, get):
        responses = {
            "/carros/marcas": [{"codigo": "1", "nome": "Marca A"}],
            "/carros/marcas/1/modelos": {
                "modelos": [{"codigo": 10, "nome": "Modelo B"}]
            },
            "/carros/marcas/1/modelos/10/anos": [
                {"codigo": "2020-1", "nome": "2020 Gasolina"}
            ],
            "/carros/marcas/1/modelos/10/anos/2020-1": {
                "Marca": "Marca A",
                "Modelo": "Modelo B",
                "AnoModelo": 2020,
                "Combustivel": "Gasolina",
                "CodigoFipe": "000001-0",
                "MesReferencia": "outubro de 2026",
                "Valor": "R$ 40.000,00",
            },
        }

        def response_for(url, **kwargs):
            self.assertEqual(kwargs["timeout"], 10)
            result = Mock()
            result.json.return_value = next(
                value for suffix, value in responses.items() if url.endswith(suffix)
            )
            return result

        get.side_effect = response_for

        initial = self.client.get("/")
        self.assertEqual(initial.status_code, 200)
        self.assertIn(b'<main>', initial.data)
        self.assertIn(b'name="brand" data-reset="model,year" disabled', initial.data)

        brand_step = self.client.get("/?vehicle_type=carros")
        self.assertIn(b"Marca A", brand_step.data)
        self.assertIn(b'name="model" data-reset="year" disabled', brand_step.data)

        model_step = self.client.get("/?vehicle_type=carros&brand=1")
        self.assertIn(b"Modelo B", model_step.data)

        year_step = self.client.get("/?vehicle_type=carros&brand=1&model=10")
        self.assertIn(b"2020 Gasolina", year_step.data)

        result = self.client.get(
            "/?vehicle_type=carros&brand=1&model=10&year=2020-1"
        )
        self.assertEqual(result.status_code, 200)
        self.assertIn("R$ 40.000,00".encode(), result.data)
        self.assertIn("Referência: outubro de 2026".encode(), result.data)
        self.assertIn(b"<dl>", result.data)

    @patch("app.requests.get")
    def test_invalid_vehicle_type_does_not_call_api(self, get):
        result = self.client.get("/?vehicle_type=invalid")
        self.assertEqual(result.status_code, 200)
        self.assertIn("Tipo de veículo inválido".encode(), result.data)
        get.assert_not_called()

    @patch("app.requests.get")
    def test_invalid_brand_does_not_request_models(self, get):
        get.return_value.json.return_value = [
            {"codigo": "1", "nome": "Marca A"}
        ]
        result = self.client.get("/?vehicle_type=carros&brand=999")
        self.assertIn("Marca inválida".encode(), result.data)
        self.assertEqual(get.call_count, 1)

    @patch("app.requests.get", side_effect=requests.Timeout)
    def test_api_failure_shows_readable_message(self, get):
        with self.assertLogs(app.logger, level="ERROR"):
            result = self.client.get("/?vehicle_type=carros")
        self.assertEqual(result.status_code, 200)
        self.assertIn("Não foi possível consultar".encode(), result.data)
        get.assert_called_once()


if __name__ == "__main__":
    unittest.main()

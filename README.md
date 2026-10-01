# Consulta FIPE

Aplicação Flask para consultar preços de referência de carros, motos e caminhões na Tabela FIPE.

## Executar localmente

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Acesse `http://localhost:5000`. A aplicação usa a API FIPE em `parallelum.com.br`. Se necessário, defina `API_KEY` no ambiente ou em um arquivo `.env` para enviar um token Bearer nas requisições. Também é possível definir `PORT` (padrão: `5000`).

Os campos são carregados em sequência. Com JavaScript desativado, o botão **Continuar** permite avançar pelas etapas.

## Testes

```powershell
python -m unittest discover -s tests -v
```

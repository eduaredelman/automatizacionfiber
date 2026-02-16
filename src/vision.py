import base64
import json
import logging
from pathlib import Path

import anthropic

import config

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

EXTRACTION_PROMPT = """Eres un experto en analisis de comprobantes de pago del Peru.
Analiza esta imagen de un comprobante/boucher de pago y extrae los datos.

Medios de pago que debes reconocer:
- Yape (app morada, logo verde/morado)
- Plin (logo azul/celeste)
- BCP (Banco de Credito, app/web naranja)
- Interbank (app/web verde)
- BBVA (app/web azul)
- Scotiabank (app/web roja)
- BanBif
- Banco de la Nacion
- Tarjeta de credito o debito
- Transferencia bancaria
- Otro

Responde UNICAMENTE con un JSON valido (sin markdown, sin texto adicional, sin ```):

{
  "es_recibo_valido": true,
  "imagen_legible": true,
  "medio_pago": "Yape|Plin|BCP|Interbank|BBVA|Scotiabank|BanBif|Banco de la Nacion|Tarjeta|Transferencia|Otro",
  "banco": "nombre del banco o app",
  "formato_comprobante": "app_movil|web|captura_pantalla|foto_pantalla|pdf|otro",
  "nombre_pagador": "nombre completo del que paga",
  "nombre_receptor": "nombre completo del que recibe",
  "monto": 0.00,
  "moneda": "PEN|USD",
  "fecha": "YYYY-MM-DD",
  "hora": "HH:MM:SS",
  "codigo_operacion": "numero de operacion o codigo de transaccion",
  "ultimos_4_digitos": "ultimos 4 digitos de cuenta o tarjeta",
  "celular_emisor": "numero de celular del que paga"
}

Reglas estrictas:
- Si la imagen NO es un comprobante de pago: "es_recibo_valido": false y todos los demas campos null.
- Si la imagen es borrosa o no se pueden leer los datos clave (monto y codigo): "imagen_legible": false.
- El monto DEBE ser un numero decimal (ejemplo: 50.00, no "S/ 50.00").
- La moneda es "PEN" para soles (S/) y "USD" para dolares ($).
- La fecha DEBE estar en formato YYYY-MM-DD.
- La hora DEBE estar en formato HH:MM:SS (24h). Si no hay hora, usa null.
- El codigo_operacion es el numero de operacion, referencia o ID de transaccion.
- Si un campo no es visible o no existe en la imagen, usa null.
- NUNCA inventes datos. Si no lo ves claramente, usa null.
"""


def extract_receipt_data(image_path: str) -> dict:
    """Extract payment data from a receipt image using Claude Vision.

    Returns a dict with all extracted fields or error info.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        logger.error(f"Image not found: {image_path}")
        return {"es_recibo_valido": False, "imagen_legible": False, "error": "Imagen no encontrada"}

    image_data = image_path.read_bytes()
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")

    suffix = image_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    media_type = media_types.get(suffix, "image/jpeg")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": EXTRACTION_PROMPT,
                        },
                    ],
                }
            ],
        )

        raw_text = response.content[0].text.strip()
        logger.info(f"Claude Vision raw response: {raw_text}")

        # Clean response in case Claude wraps it in markdown
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

        data = json.loads(raw_text)
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e} | raw: {raw_text}")
        return {"es_recibo_valido": False, "imagen_legible": False, "error": "No se pudo interpretar la respuesta"}
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return {"es_recibo_valido": False, "imagen_legible": False, "error": f"Error de API: {e}"}

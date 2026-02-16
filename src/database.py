import logging
import sqlite3
from datetime import datetime

import config

logger = logging.getLogger(__name__)

DB_PATH = str(config.DB_PATH)


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the transactions table if it doesn't exist."""
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_operacion TEXT NOT NULL,
                medio_pago TEXT,
                banco TEXT,
                monto REAL,
                moneda TEXT DEFAULT 'PEN',
                nombre_pagador TEXT,
                telefono_cliente TEXT,
                fecha_pago TEXT,
                hora_pago TEXT,
                fecha_registro TEXT NOT NULL,
                imagen_archivo TEXT,
                estado TEXT DEFAULT 'registrado'
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_codigo_operacion
            ON transacciones(codigo_operacion)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_telefono
            ON transacciones(telefono_cliente)
        """)
        conn.commit()
        logger.info("Database initialized successfully")
    finally:
        conn.close()


def is_duplicate(codigo_operacion: str) -> bool:
    """Check if a transaction code has already been processed."""
    if not codigo_operacion:
        return False

    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM transacciones WHERE codigo_operacion = ?",
            (str(codigo_operacion),),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def save_transaction(data: dict) -> int:
    """Save a processed transaction. Returns the row ID."""
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO transacciones
                (codigo_operacion, medio_pago, banco, monto, moneda,
                 nombre_pagador, telefono_cliente, fecha_pago, hora_pago,
                 fecha_registro, imagen_archivo, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("codigo_operacion", ""),
                data.get("medio_pago"),
                data.get("banco"),
                data.get("monto"),
                data.get("moneda", "PEN"),
                data.get("nombre_pagador"),
                data.get("telefono_cliente"),
                data.get("fecha"),
                data.get("hora"),
                datetime.now().isoformat(),
                data.get("imagen_archivo"),
                data.get("estado", "registrado"),
            ),
        )
        conn.commit()
        row_id = cursor.lastrowid
        logger.info(f"Transaction saved: id={row_id}, code={data.get('codigo_operacion')}")
        return row_id
    finally:
        conn.close()


def get_transactions_by_phone(telefono: str) -> list[dict]:
    """Get all transactions for a phone number."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM transacciones WHERE telefono_cliente = ? ORDER BY id DESC",
            (telefono,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# Initialize DB on module import
init_db()

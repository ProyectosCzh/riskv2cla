"""
SmartRisk - Risk Quiz Configuration
Quiz questions and profile classification logic.
"""

QUESTIONS = [
    {
        "id": "q1",
        "question": "¿Cuál es tu principal objetivo de inversión?",
        "options": [
            ("Preservar mi capital ante todo. No quiero perder lo que invertí.", 1),
            ("Obtener un crecimiento moderado, aceptando cierta volatilidad.", 2),
            ("Maximizar el crecimiento a largo plazo, aunque implique grandes fluctuaciones.", 3),
        ],
    },
    {
        "id": "q2",
        "question": "Si tu portafolio pierde un 20% de su valor en 3 meses, ¿qué harías?",
        "options": [
            ("Vendería todo para evitar mayores pérdidas.", 1),
            ("Me preocuparía, pero esperaría a que se recupere.", 2),
            ("Es una oportunidad. Compraría más activos a precio bajo.", 3),
        ],
    },
    {
        "id": "q3",
        "question": "¿En cuánto tiempo planeas necesitar este dinero?",
        "options": [
            ("Menos de 2 años. Podría necesitarlo pronto.", 1),
            ("Entre 3 y 7 años. Es una inversión de mediano plazo.", 2),
            ("Más de 10 años. Es para mi jubilación o metas de largo plazo.", 3),
        ],
    },
    {
        "id": "q4",
        "question": "¿Cuánta experiencia tienes invirtiendo en mercados financieros?",
        "options": [
            ("Ninguna o muy poca. Soy principiante.", 1),
            ("Tengo experiencia con acciones, fondos o ETFs.", 2),
            ("Soy inversor experimentado. Conozco derivados, commodities, crypto.", 3),
        ],
    },
    {
        "id": "q5",
        "question": "¿Qué escenario de inversión te resulta más atractivo?",
        "options": [
            ("Ganar un 4% anual con certeza casi absoluta (bonos del gobierno).", 1),
            ("Ganar un 10% anual en promedio, con posibles caídas del 15%.", 2),
            ("Ganar hasta un 25% anual, aceptando posibles pérdidas del 40% o más.", 3),
        ],
    },
]


def classify_profile(score: int) -> str:
    if score <= 7:
        return "conservador"
    elif score <= 12:
        return "moderado"
    else:
        return "agresivo"

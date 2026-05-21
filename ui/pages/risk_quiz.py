"""
SmartRisk - Risk Profile Quiz Page
"""
import streamlit as st
from auth.session_manager import get_current_user
from database.repositories import save_risk_profile, get_risk_profile_for_user
from ui.components.metrics_cards import page_header, section_header, alert_box, spacer


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


def _classify_profile(score: int) -> str:
    if score <= 7:
        return "conservador"
    elif score <= 12:
        return "moderado"
    else:
        return "agresivo"


def render_risk_quiz() -> None:
    user = get_current_user()
    if not user:
        return

    page_header("Perfil de Riesgo 🎯", "Responde 5 preguntas para descubrir tu perfil de inversor.")

    existing = get_risk_profile_for_user(user["id"])
    if existing:
        import json
        from pathlib import Path
        profiles_path = Path(__file__).resolve().parent.parent.parent / "config" / "risk_profiles.json"
        with open(profiles_path) as f:
            profiles = json.load(f)

        profile_key = existing["profile"]
        profile_data = profiles.get(profile_key, {})

        alert_box(
            f"{profile_data.get('icon','')} Tu perfil actual es <strong>{profile_data.get('label','')}</strong> "
            f"(score: {existing['score']} pts). Puedes retomar el quiz para actualizarlo.",
            "info",
        )
        spacer(0.5)
        if not st.checkbox("Quiero retomar el quiz"):
            _show_profile_detail(profile_key, profile_data, existing["score"])
            return

    _render_quiz_form(user["id"])


def _render_quiz_form(user_id: str) -> None:
    section_header("Cuestionario de Perfil de Riesgo", "Selecciona la respuesta que mejor describe tu situación.")

    answers = []
    valid = True

    for i, q in enumerate(QUESTIONS):
        st.markdown(
            f"""
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px;
                        padding:1.1rem 1.25rem; margin-bottom:0.75rem;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
                <div style="font-weight:600; color:#1B3A6B; font-size:0.95rem; margin-bottom:0.6rem;">
                    {i+1}. {q['question']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        option_labels = [opt[0] for opt in q["options"]]
        choice = st.radio(
            label=f"Pregunta {i+1}",
            options=option_labels,
            key=f"quiz_{q['id']}",
            label_visibility="collapsed",
        )
        score_map = {label: score for label, score in q["options"]}
        answers.append(score_map[choice])

    spacer()

    if st.button("📊 Calcular mi Perfil de Riesgo", type="primary", use_container_width=True):
        total_score = sum(answers)
        profile = _classify_profile(total_score)
        save_risk_profile(user_id, profile, total_score, answers)

        import json
        from pathlib import Path
        profiles_path = Path(__file__).resolve().parent.parent.parent / "config" / "risk_profiles.json"
        with open(profiles_path) as f:
            profiles = json.load(f)

        profile_data = profiles.get(profile, {})
        st.success(f"✅ Perfil guardado exitosamente: **{profile_data.get('label','')}**")
        st.rerun()


def _show_profile_detail(profile_key: str, profile_data: dict, score: int) -> None:
    import json
    from pathlib import Path

    col1, col2 = st.columns([1, 2])
    with col1:
        colors = {"conservador": "#C6F6D5", "moderado": "#BEE3F8", "agresivo": "#FED7D7"}
        text_colors = {"conservador": "#22543D", "moderado": "#2A4365", "agresivo": "#742A2A"}
        bg = colors.get(profile_key, "#EEF2F9")
        tc = text_colors.get(profile_key, "#1A202C")
        st.markdown(
            f"""
            <div style="background:{bg}; border-radius:16px; padding:2rem; text-align:center;">
                <div style="font-size:3rem; margin-bottom:0.75rem;">{profile_data.get('icon','⚖️')}</div>
                <div style="font-size:1.3rem; font-weight:800; color:{tc}; margin-bottom:0.5rem;">
                    {profile_data.get('label','')}
                </div>
                <div style="font-size:0.85rem; color:{tc}; opacity:0.7;">
                    Puntuación: {score}/15
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:1.5rem;
                        box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                <div style="font-size:0.9rem; color:#4A5568; line-height:1.8; margin-bottom:1rem;">
                    {profile_data.get('description','')}
                </div>
                <div style="font-size:0.8rem; color:#718096;">
                    <strong>Volatilidad máxima recomendada:</strong>
                    {int(profile_data.get('max_volatility', 0) * 100)}% anual
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    spacer()
    section_header("Activos Sugeridos para tu Perfil")
    tickers = profile_data.get("suggested_tickers", [])
    cols = st.columns(len(tickers))
    for i, ticker in enumerate(tickers):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background:#EBF4FF; border:1px solid #BEE3F8; border-radius:8px;
                            padding:0.6rem; text-align:center;">
                    <div style="font-weight:700; color:#1B3A6B;">{ticker}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

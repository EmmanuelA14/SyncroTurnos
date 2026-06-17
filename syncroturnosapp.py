import streamlit as st
import cohere
import json

# 1. Validación y conexión con Cohere
try:
    api_key = st.secrets["COHERE_API_KEY"]
    co = cohere.Client(api_key)
except Exception:
    st.error("Error: Falta configurar la variable 'COHERE_API_KEY' en los secretos de Streamlit.")
    st.stop()

# 2. Componentes obligatorios de la interfaz gráfica
st.title("SyncroTurnos 🗓️")
st.subheader("Automatización de Agendas mediante Inteligencia Artificial")

st.markdown("""
Esta herramienta permite a los clientes de trabajadores independientes y profesionales autogestionar 
sus turnos de manera directa enviando un único mensaje en lenguaje común, eliminando las respuestas manuales por WhatsApp.
""")

with st.expander("ℹ️ ¿Cómo funciona nuestro producto? ¡Aprende a usarlo!"):
    st.write("""
    1. **Escribe tu solicitud:** En el recuadro inferior, redacta de forma libre el turno que necesitas. 
       * *Ejemplo:* "Necesito reservar un turno para consulta con el psicólogo este próximo martes por la mañana, preferentemente a las 10:00 hs".
    2. **Extracción con IA:** El motor de Procesamiento de Lenguaje Natural procesará tu intención y extraerá de manera exacta los datos críticos.
    3. **Resultado y Pago:** El sistema validará la disponibilidad en la base de datos y te derivará de forma directa para abonar la seña obligatoria.
    """)

mensaje_usuario = st.text_area("Ingresa los detalles de tu turno en lenguaje natural:", 
                               placeholder="Ej: Quiero una sesión estética para este viernes por la tarde a partir de las 16hs...")

# 3. Componente: Botón de acción
if st.button("Procesar y Agendar Turno 🚀"):
    if not mensaje_usuario.strip():
        st.warning("Por favor, introduce un mensaje de texto para que la IA pueda procesarlo.")
    else:
        with st.spinner("Analizando semánticamente la solicitud..."):
            
            prompt_sistema = (
                "Role: Actúas como un asistente de agenda virtual automatizado e integrado en la plataforma SyncroTurnos.\n"
                "Instrucciones Críticas:\n"
                "1. Analiza semánticamente el texto del usuario y extrae de forma precisa las variables de reserva:\n"
                "   - 'servicio': Nombre de la prestación requerida (ej. consulta, corte, estética).\n"
                "   - 'fecha': Fecha del turno estructurada en formato estricto ISO 'AAAA-MM-DD'. Contexto actual: 2026.\n"
                "   - 'hora': Horario específico o rango de preferencia declarado.\n"
                "2. Tu salida debe ser única y exclusivamente un objeto JSON válido con las claves indicadas: 'servicio', 'fecha' y 'hora'.\n"
                "3. Si los datos son insuficientes, asígnale el valor null al atributo correspondiente.\n"
                "4. Restricción absoluta: No incluyas explicaciones, Markdown, ni texto fuera del objeto JSON."
            )
            
            try:
                # Consumo de la API de Cohere
                response = co.chat(
                    model="command-r-08-2024",
                    preamble=prompt_sistema,
                    message=mensaje_usuario,
                    temperature=0.0
                )
                
                # Limpieza por si el modelo agrega tildes invertidas de Markdown
                resultado_texto = response.text.strip()
                if resultado_texto.startswith("```json"):
                    resultado_texto = resultado_texto.replace("```json", "").replace("```", "").strip()
                elif resultado_texto.startswith("```"):
                    resultado_texto = resultado_texto.replace("```", "").strip()

                resultado_json = json.loads(resultado_texto)
                
                st.success("¡Análisis completado! La IA devolvió la siguiente estructura dirigida:")
                st.json(resultado_json)
                
                if resultado_json.get("servicio") and resultado_json.get("fecha") and resultado_json.get("hora"):
                    st.info("🔄 Redirección automatizada: Conectando con Mercado Pago para procesar el cobro de la seña...")
                else:
                    st.warning("⚠️ Datos insuficientes. El asistente asignó valores nulos debido a la ambigüedad. Intente detallar el servicio, la fecha o la hora.")
                    
            except json.JSONDecodeError:
                st.error("Error: El modelo no devolvió un formato JSON válido. Respuesta cruda: " + response.text)
            except Exception as e:
                st.error(f"Error técnico durante la comunicación con el LLM: {e}")
import streamlit as st
import cohere
import json

# 1. Validación y conexión con los Secretos de la plataforma
try:
    api_key = st.secrets["COHERE_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("Error: Falta configurar la variable 'OPENAI_API_KEY' en los secretos de Streamlit.")
    st.stop()

# 2. Componentes obligatorios de la interfaz gráfica (Requisitos de Consigna)
st.title("SyncroTurnos 🗓️")
st.subheader("Automatización de Agendas mediante Inteligencia Artificial")

st.markdown("""
Esta herramienta permite a los clientes de trabajadores independientes y profesionales autogestionar 
sus turnos de manera directa enviando un único mensaje en lenguaje común, eliminando las respuestas manuales por WhatsApp.
""")

# Componente: Sección de "cómo funciona"
with st.expander("ℹ️ ¿Cómo funciona nuestro producto? ¡Aprende a usarlo!"):
    st.write("""
    1. **Escribe tu solicitud:** En el recuadro inferior, redacta de forma libre el turno que necesitas. 
       * *Ejemplo:* "Necesito reservar un turno para consulta con el psicólogo este próximo martes por la mañana, preferentemente a las 10:00 hs".
    2. **Extracción con IA:** El motor de Procesamiento de Lenguaje Natural procesará tu intención y extraerá de manera exacta los datos críticos.
    3. **Resultado y Pago:** El sistema validará la disponibilidad en la base de datos y te derivará de forma directa para abonar la seña obligatoria.
    """)

# Entrada de datos (Mensaje de texto libre del cliente final)
mensaje_usuario = st.text_area("Ingresa los detalles de tu turno en lenguaje natural:", 
                               placeholder="Ej: Quiero una sesión estética para este viernes por la tarde a partir de las 16hs...")

# 3. Componente: Botón de acción para ejecutar la tarea específica
if st.button("Procesar y Agendar Turno 🚀"):
    if not mensaje_usuario.strip():
        st.warning("Por favor, introduce un mensaje de texto para que la IA pueda procesarlo.")
    else:
        with st.spinner("Analizando semánticamente la solicitud..."):
            
            # Recuperación e integración del Prompt Inicial Estructurado de la Preentrega
            prompt_sistema = (
                "Role: Actúas como un asistente de agenda virtual automatizado e integrado en la plataforma SyncroTurnos.\n"
                "Contexto: El cliente final de un prestador de servicios ha ingresado el siguiente mensaje de texto libre.\n"
                "Instrucciones Críticas:\n"
                "1. Analiza semánticamente el texto proporcionado y extrae de forma precisa las variables de reserva:\n"
                "   - 'servicio': Nombre de la prestación requerida (ej. consulta, corte, estética).\n"
                "   - 'fecha': Fecha del turno estructurada en formato estricto ISO 'AAAA-MM-DD'. Si el usuario hace referencia a un día de la semana relativo (ej. 'este viernes'), calcula la fecha exacta basándote en el contexto actual del año 2026.\n"
                "   - 'hora': Horario específico o rango de preferencia declarado.\n"
                "2. Tu salida debe ser única y exclusivamente un objeto JSON válido con las claves indicadas: 'servicio', 'fecha' y 'hora'.\n"
                "3. Si los datos provistos en el mensaje son insuficientes o ambiguos para deducir con certeza alguna de las claves, asígnale el valor null al atributo correspondiente.\n"
                "4. Restricción absoluta: No incluyas explicaciones, introducciones, saludos ni etiquetas tipográficas Markdown fuera del objeto JSON."
            )
            
            try:
                # Consumo de la API con especificación de salida JSON estricta (Structured Outputs)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": f"Mensaje del usuario: '{mensaje_usuario}'"}
                    ],
                    temperature=0.0
                )
                
                # Parsear y decodificar la salida dirigida
                resultado_texto = response.choices[0].message.content
                resultado_json = json.loads(resultado_texto)
                
                # Despliegue de los datos estructurados en la interfaz
                st.success("¡Análisis completado! La IA devolvió la siguiente estructura dirigida:")
                st.json(resultado_json)
                
                # Validación de flujo de negocio (Pasarela Mercado Pago)
                if resultado_json.get("servicio") and resultado_json.get("fecha") and resultado_json.get("hora"):
                    st.info("🔄 Redirección automatizada: Conectando con Mercado Pago para procesar el cobro de la seña mínima obligatoria...")
                else:
                    st.warning("⚠️ Datos insuficientes. El asistente asignó valores nulos debido a la ambigüedad. Intente detallar el servicio, la fecha o la hora.")
                    
            except Exception as e:
                st.error(f"Error técnico durante la comunicación con el LLM: {e}")
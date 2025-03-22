import streamlit as st
import pandas as pd
from google import genai
import json

# Configure Google Gemini AI
client = genai.Client(api_key='AIzaSyAcP9xNP6zwTIyPLNh2JGWPrsw9CdIo6mw')
model = 'gemini-2.0-flash'

# Initialize session state variables if they don't exist
if 'volunteers' not in st.session_state:
    st.session_state.volunteers = []
if 'organizations' not in st.session_state:
    st.session_state.organizations = []
if 'matches' not in st.session_state:
    st.session_state.matches = []

# Function to generate AI-based matches
def generate_matches():
    if not st.session_state.volunteers or not st.session_state.organizations:
        st.warning("Por favor, añade al menos un voluntario y una organización para generar coincidencias.")
        return []
    
    # Prepare data for AI matching
    volunteers_data = json.dumps(st.session_state.volunteers)
    organizations_data = json.dumps(st.session_state.organizations)
    
    prompt = f"""
    Tengo los siguientes voluntarios con sus habilidades e intereses:
    {volunteers_data}
    
    Y estas organizaciones con sus necesidades y misiones:
    {organizations_data}
    
    Por favor, empareja cada voluntario con la organización más adecuada basándote en:
    1. Alineación de las habilidades del voluntario con las necesidades de la organización
    2. Compatibilidad de los intereses del voluntario con la misión de la organización
    3. Potencial para una contribución significativa
    
    Para cada coincidencia, proporciona:
    - Nombre del voluntario
    - Nombre de la organización
    - Puntuación de compatibilidad (0-100)
    - Breve explicación de por qué es una buena coincidencia
    
    Devuelve los resultados como un array JSON de objetos con los campos: volunteer_name, organization_name, match_score, explanation.
    Asegúrate de que la explicación esté en español.
    """
    
    try:
        response = client.models.generate_content(
            model=model,
            content=prompt
        )
        
        # Extract JSON from response
        response_text = response.text
        # Find JSON content between ```json and ``` if present
        if "```json" in response_text and "```" in response_text.split("```json")[1]:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        else:
            # Otherwise try to find any JSON array in the response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text
        
        matches = json.loads(json_str)
        return matches
    except Exception as e:
        st.error(f"Error al generar coincidencias: {str(e)}")
        return []

# App title and description
st.title("VolunNet")
st.subheader("Conectando Voluntarios y Organizaciones con IA")
st.markdown("""
VolunNet ayuda a conectar voluntarios apasionados con organizaciones que necesitan sus habilidades.
Nuestro sistema de emparejamiento impulsado por IA encuentra las oportunidades perfectas para una contribución significativa.
""")

# Main navigation
tab1, tab2, tab3 = st.tabs(["Voluntarios", "Organizaciones", "Coincidencias"])

# Volunteer Tab
with tab1:
    st.header("Registro de Voluntarios")
    
    # Volunteer form
    with st.form("volunteer_form"):
        vol_name = st.text_input("Nombre Completo")
        vol_email = st.text_input("Correo Electrónico")
        vol_skills = st.multiselect(
            "Habilidades",
            ["Programación", "Diseño", "Redacción", "Enseñanza", "Marketing", 
             "Planificación de Eventos", "Recaudación de Fondos", "Liderazgo", "Administración",
             "Redes Sociales", "Investigación", "Oratoria", "Traducción"]
        )
        vol_interests = st.text_area("Intereses y Causas que te Importan")
        vol_availability = st.selectbox(
            "Disponibilidad",
            ["Solo fines de semana", "Tardes entre semana", "Tiempo completo", "Tiempo parcial", "Flexible"]
        )
        vol_experience = st.slider("Años de Experiencia", 0, 20, 1)
        
        submitted = st.form_submit_button("Registrarse como Voluntario")
        if submitted and vol_name and vol_email:
            new_volunteer = {
                "name": vol_name,
                "email": vol_email,
                "skills": vol_skills,
                "interests": vol_interests,
                "availability": vol_availability,
                "experience": vol_experience
            }
            st.session_state.volunteers.append(new_volunteer)
            st.success(f"¡Gracias {vol_name}! Tu perfil de voluntario ha sido registrado.")
    
    # Display registered volunteers
    if st.session_state.volunteers:
        st.subheader("Voluntarios Registrados")
        vol_df = pd.DataFrame(st.session_state.volunteers)
        st.dataframe(vol_df)
    
    # Option to clear volunteers (for demo purposes)
    if st.session_state.volunteers and st.button("Borrar Todos los Voluntarios"):
        st.session_state.volunteers = []
        st.experimental_rerun()

# Organization Tab
with tab2:
    st.header("Registro de Organizaciones")
    
    # Organization form
    with st.form("organization_form"):
        org_name = st.text_input("Nombre de la Organización")
        org_mission = st.text_area("Declaración de Misión")
        org_needs = st.multiselect(
            "Necesidades de Voluntarios",
            ["Programación", "Diseño", "Redacción", "Enseñanza", "Marketing", 
             "Planificación de Eventos", "Recaudación de Fondos", "Liderazgo", "Administración",
             "Redes Sociales", "Investigación", "Oratoria", "Traducción"]
        )
        org_description = st.text_area("Descripción de Oportunidades para Voluntarios")
        org_location = st.text_input("Ubicación")
        org_website = st.text_input("Sitio Web (opcional)")
        
        submitted = st.form_submit_button("Registrar Organización")
        if submitted and org_name and org_mission:
            new_organization = {
                "name": org_name,
                "mission": org_mission,
                "needs": org_needs,
                "description": org_description,
                "location": org_location,
                "website": org_website
            }
            st.session_state.organizations.append(new_organization)
            st.success(f"¡{org_name} ha sido registrada exitosamente!")
    
    # Display registered organizations
    if st.session_state.organizations:
        st.subheader("Organizaciones Registradas")
        org_df = pd.DataFrame(st.session_state.organizations)
        st.dataframe(org_df)
    
    # Option to clear organizations (for demo purposes)
    if st.session_state.organizations and st.button("Borrar Todas las Organizaciones"):
        st.session_state.organizations = []
        st.experimental_rerun()

# Matches Tab
with tab3:
    st.header("Coincidencias Impulsadas por IA")
    
    if st.button("Generar Coincidencias"):
        with st.spinner("La IA está encontrando las mejores coincidencias..."):
            matches = generate_matches()
            st.session_state.matches = matches
    
    # Display matches
    if st.session_state.matches:
        for match in st.session_state.matches:
            with st.expander(f"{match['volunteer_name']} ↔ {match['organization_name']} (Puntuación: {match['match_score']})"):
                st.markdown(f"**Explicación de la Coincidencia:** {match['explanation']}")
                
                # Find the volunteer and organization details
                volunteer = next((v for v in st.session_state.volunteers if v['name'] == match['volunteer_name']), None)
                organization = next((o for o in st.session_state.organizations if o['name'] == match['organization_name']), None)
                
                if volunteer and organization:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Voluntario")
                        st.write(f"**Nombre:** {volunteer['name']}")
                        st.write(f"**Habilidades:** {', '.join(volunteer['skills'])}")
                        st.write(f"**Intereses:** {volunteer['interests']}")
                        st.write(f"**Disponibilidad:** {volunteer['availability']}")
                    
                    with col2:
                        st.subheader("Organización")
                        st.write(f"**Nombre:** {organization['name']}")
                        st.write(f"**Misión:** {organization['mission']}")
                        st.write(f"**Necesidades:** {', '.join(organization['needs'])}")
                        if organization['website']:
                            st.write(f"**Sitio Web:** {organization['website']}")
    else:
        st.info("Haz clic en 'Generar Coincidencias' para encontrar los mejores pares de voluntarios y organizaciones.")

# Sidebar with app info and tips
with st.sidebar:
    st.header("Acerca de VolunNet")
    st.markdown("""
    VolunNet utiliza IA para crear conexiones significativas entre voluntarios y organizaciones.
    
    **Cómo funciona:**
    1. Los voluntarios registran sus habilidades e intereses
    2. Las organizaciones enumeran sus necesidades y misiones
    3. Nuestra IA analiza los datos para encontrar coincidencias óptimas
    4. Ambas partes se conectan para una colaboración impactante
    """)
    
    st.divider()
    
    st.subheader("Consejos para Mejores Coincidencias")
    st.markdown("""
    - Sé específico sobre habilidades y necesidades
    - Proporciona descripciones detalladas
    - Actualiza tu perfil regularmente
    - Comunícate rápidamente cuando haya una coincidencia
    """)

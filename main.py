import streamlit as st
import pandas as pd
import json
from dotenv import load_dotenv
import os
import re
from typing import List, Dict, Any

# Cargar variables de entorno
load_dotenv()

# Initialize session state variables if they don't exist
if 'volunteers' not in st.session_state:
    st.session_state.volunteers = []
if 'organizations' not in st.session_state:
    st.session_state.organizations = []
if 'matches' not in st.session_state:
    st.session_state.matches = []

def validate_email(email: str) -> bool:
    """Valida el formato del correo electrónico."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_duplicate_volunteer(email: str) -> bool:
    """Verifica si ya existe un voluntario con el mismo correo."""
    return any(v['email'] == email for v in st.session_state.volunteers)

def is_duplicate_organization(name: str) -> bool:
    """Verifica si ya existe una organización con el mismo nombre."""
    return any(o['name'] == name for o in st.session_state.organizations)

def calculate_match_score(volunteer: Dict, organization: Dict) -> int:
    """Calcula la puntuación de coincidencia entre un voluntario y una organización."""
    score = 0
    
    # Coincidencia de habilidades (40 puntos)
    matching_skills = set(volunteer['skills']) & set(organization['needs'])
    if matching_skills:
        score += min(40, len(matching_skills) * 10)
    
    # Experiencia del voluntario (20 puntos)
    if volunteer['experience'] > 0:
        score += min(20, volunteer['experience'])
    
    # Disponibilidad (20 puntos)
    if volunteer['availability'] in ["Tiempo completo", "Flexible"]:
        score += 20
    elif volunteer['availability'] in ["Tardes entre semana", "Tiempo parcial"]:
        score += 15
    elif volunteer['availability'] == "Solo fines de semana":
        score += 10
    
    # Intereses y misión (20 puntos)
    if volunteer['interests'] and organization['mission']:
        # Buscar palabras clave comunes
        volunteer_keywords = set(volunteer['interests'].lower().split())
        mission_keywords = set(organization['mission'].lower().split())
        common_keywords = volunteer_keywords & mission_keywords
        if common_keywords:
            score += min(20, len(common_keywords) * 5)
    
    return score

def generate_matches():
    """Genera coincidencias entre voluntarios y organizaciones usando un algoritmo basado en reglas."""
    if not st.session_state.volunteers or not st.session_state.organizations:
        st.warning("Por favor, añade al menos un voluntario y una organización para generar coincidencias.")
        return []
    
    matches = []
    for volunteer in st.session_state.volunteers:
        for organization in st.session_state.organizations:
            score = calculate_match_score(volunteer, organization)
            if score > 0:  # Solo incluir coincidencias con puntuación mayor a 0
                # Generar explicación basada en los criterios de coincidencia
                explanation_parts = []
                
                # Coincidencia de habilidades
                matching_skills = set(volunteer['skills']) & set(organization['needs'])
                if matching_skills:
                    explanation_parts.append(f"Coincidencia de habilidades: {', '.join(matching_skills)}")
                
                # Experiencia
                if volunteer['experience'] > 0:
                    explanation_parts.append(f"El voluntario tiene {volunteer['experience']} años de experiencia")
                
                # Disponibilidad
                explanation_parts.append(f"Disponibilidad: {volunteer['availability']}")
                
                # Intereses y misión
                if volunteer['interests'] and organization['mission']:
                    volunteer_keywords = set(volunteer['interests'].lower().split())
                    mission_keywords = set(organization['mission'].lower().split())
                    common_keywords = volunteer_keywords & mission_keywords
                    if common_keywords:
                        explanation_parts.append(f"Intereses alineados con la misión: {', '.join(common_keywords)}")
                
                matches.append({
                    "volunteer_name": volunteer['name'],
                    "organization_name": organization['name'],
                    "match_score": score,
                    "explanation": " | ".join(explanation_parts)
                })
    
    # Ordenar coincidencias por puntuación
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches

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
        if submitted:
            if not vol_name or not vol_email:
                st.error("Por favor, completa todos los campos obligatorios.")
            elif not validate_email(vol_email):
                st.error("Por favor, ingresa un correo electrónico válido.")
            elif is_duplicate_volunteer(vol_email):
                st.error("Ya existe un voluntario registrado con este correo electrónico.")
            else:
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
        st.session_state.clear()
        st.rerun()

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
        if submitted:
            if not org_name or not org_mission:
                st.error("Por favor, completa todos los campos obligatorios.")
            elif is_duplicate_organization(org_name):
                st.error("Ya existe una organización registrada con este nombre.")
            else:
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
        st.session_state.clear()
        st.rerun()

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

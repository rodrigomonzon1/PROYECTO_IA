# VolunNet - Plataforma de Emparejamiento de Voluntarios con IA

VolunNet es una aplicación web que utiliza inteligencia artificial para conectar voluntarios con organizaciones sin fines de lucro, basándose en habilidades, intereses y necesidades.

## Características

- Registro de voluntarios con habilidades e intereses
- Registro de organizaciones con necesidades y misiones
- Sistema de emparejamiento impulsado por IA
- Interfaz intuitiva y fácil de usar
- Visualización detallada de coincidencias

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona este repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd [NOMBRE_DEL_DIRECTORIO]
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Crea un archivo `.env` en la raíz del proyecto y añade tu API key de Google:
```
GOOGLE_API_KEY=tu_api_key_aquí
```

## Uso

1. Inicia la aplicación:
```bash
streamlit run main.py
```

2. Abre tu navegador y visita `http://localhost:8501`

3. Comienza a registrar voluntarios y organizaciones

4. Utiliza la pestaña "Coincidencias" para generar emparejamientos con IA

## Estructura del Proyecto

- `main.py`: Archivo principal de la aplicación
- `requirements.txt`: Lista de dependencias
- `.env`: Archivo de configuración para variables de entorno (no incluido en el repositorio)
- `.gitignore`: Archivo para excluir archivos sensibles del control de versiones

## Contribuir

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 
# Orquestador de Cripto IA

## 1. Visión General

El Orquestador de Cripto IA es un sofisticado sistema de desarrollo de IA multi-agente, diseñado para automatizar y mejorar la creación de proyectos de software complejos, particularmente en los dominios de las finanzas descentralizadas (DeFi), la computación cuántica y nuevos paradigmas revolucionarios. Aprovecha un conjunto de agentes de IA especializados para realizar tareas de desarrollo de forma concurrente, gestionados por un orquestador central.

Este proyecto ha sido elevado a un nivel avanzado, incorporando agentes conceptuales "xuabgicos" y un sistema de integración simbiótica para facilitar la colaboración entre agentes a través de un contexto compartido.

## 2. Conceptos Clave

- **Orquestador**: El script central de Python (`crypto_ai_orchestrator.py`) que gestiona todo el flujo de trabajo. Analiza los comandos del usuario, crea las estructuras de los proyectos y despacha las tareas a los agentes de IA apropiados.
- **Agentes de IA**: Herramientas externas de IA basadas en la línea de comandos que realizan tareas de desarrollo específicas. El orquestador está preconfigurado para trabajar con agentes como `smol-developer`, `aider` y `shell-gpt`. También incluye agentes conceptuales como `quantum-agent` y `xuabgicos-agent` para futuras aplicaciones.
- **Plantillas de Proyecto**: Estructuras de proyecto y diseños de archivos predefinidos para diferentes tipos de proyectos (ej. `defi`, `quantum`, `revolution`, `xuabgicos`). Se definen en `config.json`.
- **Integración Simbiótica**: Los agentes pueden compartir información y contexto a través de un archivo `context.json` compartido dentro del directorio `memory` de cada proyecto, permitiendo una colaboración más estrecha.
- **Ejecución Asíncrona**: El orquestador ejecuta los agentes de IA de forma concurrente utilizando la biblioteca `asyncio` de Python, acelerando significativamente el proceso de desarrollo.
- **Registro e Historial**: El sistema mantiene registros detallados de todas las operaciones en `orchestrator.log` y guarda un registro de cada tarea de orquestación en el directorio `memory/`.

## 3. Cómo Empezar

### 3.1. Prerrequisitos

- Python 3.7+
- Los agentes de IA que se pretenda utilizar deben estar instalados y disponibles en el PATH del sistema.

### 3.2. Instalación y Ejecución

El script `crypto-ai-orchestrator.sh` se encarga de la configuración del entorno y la ejecución.

1.  Asegúrate de que el script `crypto-ai-orchestrator.sh` tenga permisos de ejecución:
    ```bash
    chmod +x crypto-ai-orchestrator.sh
    ```
2.  Ejecuta el script. Automáticamente creará un entorno virtual de Python, instalará las dependencias (si las hubiera en `requirements.txt`) y ejecutará el orquestador.

### 3.3. Configuración

Modifica el archivo `config.json` para personalizar el comportamiento del orquestador:

- `default_agents`: Una lista de agentes a utilizar si no se especifican en el comando.
- `timeout_seconds`: El número de segundos a esperar antes de que una tarea de un agente se considere agotada.
- `initial_file_contents`: Contenido por defecto que se colocará en los archivos recién creados según su extensión.
- `project_templates`: Define la estructura y los archivos para los diferentes tipos de proyecto.

## 4. Uso

La forma principal de interactuar con el orquestador es a través del script `crypto-ai-orchestrator.sh`.

### 4.1. Orquestar un Nuevo Proyecto

Para iniciar una nueva tarea de desarrollo, utiliza el comando `orchestrate`.

**Sintaxis:**

```bash
./crypto-ai-orchestrator.sh orchestrate --task "Tu descripción de la tarea de desarrollo" [OPCIONES]
```

**Argumentos:**

- `--task`: (Requerido) Una cadena que describe la tarea de desarrollo para los agentes de IA.
- `--project-type`: El tipo de proyecto a crear (ej. `defi`, `quantum`, `xuabgicos`). Por defecto es `revolution`.
- `--agents`: Una lista de agentes separados por espacios a utilizar (ej. `smol-developer aider`). Por defecto, los agentes de `config.json`.
- `--project-path`: Un nombre específico para la carpeta del proyecto. Si no se proporciona, se generará un nombre basado en la tarea y la marca de tiempo.

**Ejemplo:**

```bash
./crypto-ai-orchestrator.sh orchestrate \
  --task "Desarrollar un algoritmo de encriptación cuantica y una red neuronal para gestionarlo" \
  --project-type "quantum" \
  --agents smol-developer quantum-agent
```

### 4.2. Ver el Historial de Orquestación

Para ver una lista de las tareas de orquestación pasadas, utiliza el comando `history`.

**Sintaxis:**

```bash
./crypto-ai-orchestrator.sh history
```

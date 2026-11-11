---
course: COMPUTACION EN INTERNET II
document_type: GUIA DE TALLER PRACTICO
title: "Taller 01: Arquitectura de Servicios y Modelo de Dominio"
period: "202620"
nrc: "12489"
group: "005"
faculty: FACULTAD DE INGENIERIA, DISENO Y CIENCIAS APLICADAS
department: DEPARTAMENTO DE COMPUTACION Y SISTEMAS INTELIGENTES
professor: Docente Encargado
due_date: 15 de Octubre de 2026
modality: Equipos (2 personas)
code: 09769 - TIC
---

## Introduccion y Objetivos de Aprendizaje

El presente taller practico tiene como objetivo afianzar los fundamentos de arquitectura limpia, desacoplamiento y diseno modular mediante la construccion de servicios transaccionales en un entorno empresarial simulado.

> [!NOTE]
> **Resultado de Aprendizaje de la Asignatura (RAA4):** Utilizar herramientas tecnologicas y marcos de diseno arquitectonico modernos para estructurar servicios web transaccionales garantizando la persistencia, escalabilidad e integridad de los datos.

Los estudiantes aplicaran patrones de repositorio, inyeccion de dependencias y separacion de responsabilidades entre la logica de dominio y la infraestructura externa.

## Arquitectura del Sistema Propuesto

La solucion a implementar debe estructurarse siguiendo el flujo desacoplado que se ilustra a continuacion:

```mermaid
flowchart LR
    Client[Cliente Web / Movil] -->|Peticion HTTP REST| Controller[Controlador REST]
    Controller -->|DTOs Validados| Service[Servicio de Aplicacion]
    Service -->|Entidades y Reglas| Domain[Modelo de Dominio]
    Service -->|Contrato de Puerto| Repo[Repositorio de Persistencia]
    Repo -->|Driver SQL| DB[(Base de Datos Transaccional)]
caption: Figura 1. Flujo de comunicacion por capas en la arquitectura propuesta.
```

## Consigna y Requerimientos de Implementacion

Cada equipo debera cumplir rigurosamente con los siguientes requerimientos tecnicos:

1. **Definicion de Contratos de Interfaz (DTOs):** Crear las clases de transferencia de datos con validaciones automaticas de esquema (longitud de cadenas, formato de correos electronicos y rangos numericos).
2. **Encapsulamiento del Modelo de Dominio:** Las entidades de dominio no deben poseer dependencias de ningun framework de infraestructura o persistencia. Toda invariante debe ser validada en el constructor o metodos de dominio.
3. **Mapeo y Persistencia:** Configurar los mapeos relacionales y las migraciones de base de datos automatizadas.
4. **Pruebas Automatizadas:** Implementar un conjunto minimo de pruebas unitarias que verifiquen las reglas de negocio criticas con una cobertura superior al 80%.

```json
{
  "status": "success",
  "data": {
    "transactionId": "tx-994812",
    "amount": 250000.0,
    "currency": "COP",
    "timestamp": "2026-10-15T10:30:00Z"
  }
}
```

> [!WARNING]
> **Regla de Integridad:** Queda terminantemente prohibido acceder a la base de datos de manera directa desde los controladores sin pasar por la capa de servicios de aplicacion.

## Politica sobre el Uso de Inteligencia Artificial Generativa (IAG)

En coherencia con el Lineamiento sobre IA y Educacion de la Universidad Icesi, este curso promueve un uso etico, critico y transparente de las herramientas de IAG.

> [!IMPORTANT]
> **Nivel de Uso Permitido: Colaboracion con IAG.**
> Se autoriza el uso de asistentes inteligentes (Claude, Gemini, ChatGPT) para consulta de documentacion, optimizacion de consultas SQL o generacion de casos de prueba. El diseno conceptual, la sustentacion oral y la justificacion arquitectonica deben ser de autoria exclusiva del equipo.

Durante la entrega, cada equipo debera anexar una declaracion que especifique que herramientas fueron utilizadas, los prompts clave empleados y las validaciones humanas realizadas sobre las respuestas obtenidas.

## Criterios de Calificacion y Rubrica de Aprendizajes

La evaluacion se realizara de forma individual y por equipo de acuerdo con los siguientes criterios:

| Criterio Evaluativo | Descripcion de Cumplimiento | Nivel IAG | Peso |
| :--- | :--- | :---: | :---: |
| **Arquitectura y Desacoplamiento** | Separacion estricta entre capas y ausencia de fugas de infraestructura hacia el dominio. | Planificacion IAG | 35% |
| **Endpoints y Controladores** | Diseno RESTful, gestion semantica de codigos HTTP y validacion de DTOs. | Colaboracion IAG | 25% |
| **Pruebas de Integracion** | Bateria de pruebas automatizadas cubriendo los casos de exito y caminos alternos. | Colaboracion IAG | 25% |
| **Informe y Declaracion IAG** | Claridad en la documentacion del README y transparencia en el uso de herramientas. | No IAG | 15% |

## Instrucciones de Entrega y Metodologia de Envio

1. La entrega se realizara mediante un enlace al repositorio en GitHub / GitLab en la plataforma institucional.
2. La rama principal (`main`) debe contener el codigo funcional y el archivo `README.md` con las instrucciones de despliegue local usando contenedores.
3. Fecha limite de entrega: **15 de Octubre de 2026, 23:59 COT**. No se aceptaran entregas extemporaneas sin excusa academica valida.

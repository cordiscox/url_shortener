# Acortador de URL con Despliegue Automatizado en AWS Fargate

Este proyecto implementa un servicio para acortar URLs, construido con FastAPI y desplegado en AWS Fargate. La infraestructura se gestiona como código usando Terraform, y el despliegue es completamente automático a través de un pipeline de CI/CD con GitHub Actions.

## Arquitectura

El flujo de trabajo está diseñado para ser simple y robusto:

1.  **Push a GitHub:** Un desarrollador sube cambios a la rama `main` del repositorio.
2.  **GitHub Actions (CI/CD):**
    * Se activa un workflow que construye una nueva imagen de Docker.
    * La imagen es etiquetada con el hash del commit y subida a un repositorio privado en **Amazon ECR**.
3.  **Terraform Apply:**
    * El mismo workflow ejecuta Terraform.
    * Terraform se conecta a un **backend en S3** para leer el estado actual de la infraestructura.
    * Detecta que la URI de la imagen ha cambiado y crea una nueva revisión de la **Definición de Tarea de ECS**.
4.  **Despliegue en Fargate:**
    * El servicio de **ECS** realiza un despliegue continuo (rolling update), reemplazando el contenedor antiguo por el nuevo sin tiempo de inactividad.
    * El tráfico es gestionado por un **Application Load Balancer (ALB)**.

---

## Cómo Funciona la API

La aplicación tiene dos endpoints principales:

### 1. Acortar una URL (`POST /shorten`)

Este endpoint recibe una URL larga y devuelve una versión corta.

**Ejemplo con `curl`:**
```bash
curl -X POST "http://<URL_DE_TU_ALB>/shorten?long_url=[https://www.wikipedia.org/wiki/Continuous_integration](https://www.wikipedia.org/wiki/Continuous_integration)"
```

**Respuesta esperada:**
```json
{
  "short_url": "http://<URL_DE_TU_ALB>/aBcDeF12"
}
```

### 2. Redirigir a la URL Larga (`GET /{short_code}`)

Este endpoint recibe un código corto y redirige al usuario a la URL larga original.

**Ejemplo con `curl`:**
```bash
# La opción -L le dice a curl que siga la redirección
curl -L "http://<URL_DE_TU_ALB>/aBcDeF12"
```

---

## Guía de Configuración Paso a Paso

Para desplegar este proyecto en tu propia cuenta de AWS, sigue estos pasos.

### Requisitos Previos

* Una cuenta de AWS.
* Un repositorio de GitHub.
* [Terraform](https://developer.hashicorp.com/terraform/downloads) instalado en tu máquina local.
* [Docker](https://www.docker.com/products/docker-desktop/) instalado en tu máquina local.

### Paso 1: Clonar el Repositorio

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

### Paso 2: Configurar Credenciales de AWS

1.  Crea un **usuario IAM** en tu cuenta de AWS con "Acceso Programático".
2.  Asígnale permisos de administrador (`AdministratorAccess`) para simplificar esta guía. En un entorno de producción, deberías usar permisos más restringidos.
3.  Guarda el **Access Key ID** y el **Secret Access Key**. Los necesitarás en el siguiente paso.

### Paso 3: Configurar Secretos en GitHub

Ve a tu repositorio de GitHub > `Settings` > `Secrets and variables` > `Actions` y crea los siguientes secretos:

* `AWS_ACCESS_KEY_ID`: El Access Key ID de tu usuario IAM.
* `AWS_SECRET_ACCESS_KEY`: El Secret Access Key de tu usuario IAM.
* `AWS_REGION`: La región de AWS que quieres usar (ej: `us-east-2`).
* `ECR_REPOSITORY_NAME`: El nombre que le darás a tu repositorio de imágenes (ej: `url-shortener`).

### Paso 4: Crear el Repositorio en ECR

1.  Ve a la consola de AWS y al servicio **Elastic Container Registry (ECR)**.
2.  Haz clic en **"Crear repositorio"**.
3.  Elige la opción **"Privado"**.
4.  En "Nombre del repositorio", usa el mismo nombre que pusiste en el secreto `ECR_REPOSITORY_NAME`.
5.  Deja el resto de las opciones por defecto y crea el repositorio.

### Paso 5: Crear el Bucket S3 para el Backend de Terraform

Esto se hace **una sola vez y de forma manual**.

1.  Ve a la consola de AWS y al servicio **S3**.
2.  Haz clic en **"Crear bucket"**.
3.  **Nombre del bucket:** Elige un nombre **único a nivel mundial** (ej: `mi-proyecto-terraform-estado-12345`). Anota este nombre.
4.  **Región:** Elige la misma región que usaste en los secretos.
5.  **Configuración de bloqueo de acceso público:** Deja todo marcado (Bloquear todo el acceso público).
6.  **Versionado de buckets:** Haz clic en **"Habilitar"**. Esto es crucial para proteger tu archivo de estado.
7.  Crea el bucket.

### Paso 6: Configurar el Archivo `backend.tf`

1.  Abre el archivo `terraform/backend.tf`.
2.  Reemplaza `TU-NOMBRE-DE-BUCKET-UNICO` con el nombre del bucket que acabas de crear.

```terraform
terraform {
  backend "s3" {
    bucket = "TU-NOMBRE-DE-BUCKET-UNICO" # <-- REEMPLAZA ESTO
    key    = "global/s3/terraform.tfstate"
    region = "us-east-2"
  }
}
```

### Paso 7: ¡Desplegar!

Ahora estás listo. Simplemente haz un `commit` y `push` de tus cambios a la rama `main`.

```bash
git add .
git commit -m "Configuración inicial del proyecto"
git push origin main
```

Esto activará el workflow de GitHub Actions, que construirá la imagen, la subirá a ECR y usará Terraform para crear toda la infraestructura en tu cuenta de AWS.

---

## Gestión de la Infraestructura

Puedes gestionar la infraestructura desde tu máquina local gracias al backend remoto en S3.

### Inicializar Terraform Localmente

Para poder ejecutar comandos de Terraform en tu computadora, primero necesitas inicializarlo.

```bash
cd terraform
terraform init
```

Terraform se conectará a tu bucket de S3 y descargará la información del estado actual.

### Destruir la Infraestructura

Para eliminar todos los recursos creados por Terraform y evitar costos, ejecuta:

```bash
# Desde la carpeta /terraform
terraform destroy
```

Terraform te mostrará todo lo que va a borrar. Escribe `yes` para confirmar.
# Evaluación CNE
Herramientas para evaluar, revisar y mejorar las actas emitidas por el sistema de votación del CNE (Venezuela)


## En qué consiste?

Algunos scripts de python para capturar las actas emitidas por el sistema de votación del CNE (Venezuela), ecualizarlas, mejorarlas y extraer la información contenida en el QR inferior.

## Instalación

Simplemente hay que crear un virtualenv de python (> 3.10), en Linux esto se hace con:

```
python -m venv .venv
```

Para luego ejecutar la instalación de los paquetes necesarios.

- En Linux:
```
make install
```

o ejecutar la instalación con pip
```
pip install -e .
```

## Configuración

Se debe crear un archivo de configuración (.env) en un directorio llamado "env" en la raiz del proyecto.

```
mkdir -p env/ && touch env/.env
```

Hay un archivo de configuración de ejemplo en /docs/config.example

Importantes son:
 * DIRECTORIO_ACTAS: Directorio donde las actas originales se han descargado.
 * DIRECTORIO_ACTAS_PROCESADAS: directorio donde las actas procesadas se almacenarán.
 * DIRECTORIO_LOG: Genera un archivo con los QR no procesados.


 ## Uso

 Un script de ejemplo de uso se encuentra en el directorio "examples":

 ```
 python examples/usage.py
 ```

Consta de dos partes,
 * el Directory Iterator, un iterador async sobre el directorio de actas.
 * el ImageProcessor: un procesador de imágenes que se usa para rotar, equilibrar y extraer el QR

 El DirectoryIterator creará la estructura de destino idéntica que la estructura origen:

 ```bash
 .
└── SUCRE
    ├── MP. ANDRES E BLANCO
    │   ├── PQ. MARIÑO
    │   └── PQ. ROMULO GALLEGOS
    ├── MP. ANDRES MATA
    │   ├── PQ. SAN JOSE DE AEROCUAR
    │   └── PQ. TAVERA ACOSTA
    ├── MP. ARISMENDI
    │   ├── PQ. ANTONIO JOSE DE SUCRE
    │   ├── PQ. EL MORRO DE PTO SANTO
    │   ├── PQ. PUERTO SANTO
    │   └── PQ. RIO CARIBE
    ├── MP. BENITEZ
    │   ├── PQ. EL PILAR
    │   ├── PQ. EL RINCON
    │   ├── PQ. GRAL FCO. A VASQUEZ
    │   ├── PQ. GUARAUNOS
    │   └── PQ. TUNAPUICITO
    ├── MP. BERMUDEZ
    │   ├── PQ. BOLIVAR
    │   ├── PQ. MACARAPANA
    │   ├── PQ. SANTA CATALINA
    │   ├── PQ. SANTA ROSA
    │   └── PQ. SANTA TERESA
    ├── MP. BOLIVAR
    │   └── CM. MARIGUITAR
    ├── MP. CAJIGAL
    │   ├── PQ. LIBERTAD
    │   ├── PQ. PAUJIL
    │   └── PQ. YAGUARAPARO

```

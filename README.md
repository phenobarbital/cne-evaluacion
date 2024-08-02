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

## Configuración y uso

Se debe crear un archivo de configuración (.env) en un directorio llamado "env" en la raiz del proyecto.

```
mkdir -p env/ && touch env/.env
```

Hay un archivo de configuración de ejemplo en /docs/config.

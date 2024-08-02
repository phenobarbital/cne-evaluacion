"""
Iterar sobre un directorio contentivo de Actas y procesarlas.
"""
import asyncio
from pathlib import Path
from navconfig.conf import (
    DIRECTORIO_ACTAS,
    DIRECTORIO_ACTAS_PROCESADAS,
    EXTENSION_ACTAS,
    DIRECTORIO_LOG
)
from cne_evaluation.directories import DirectoryIterator
from cne_evaluation.images import ImageProcessor

async def process_images(directory, destination, extensions):
    """_summary_

    Args:
        directory (str): directory where images resides.
        extensions (list): List of available extensions.
    """
    dir_iterator = DirectoryIterator(directory, destination, extensions)
    async for _, destination_path, image_path in dir_iterator:
        # 1.- crear directorio (si no existe)
        dir_iterator.make_dir(destination_path)
        # 2.- Invocar al procesador de imágenes:
        async with ImageProcessor(
            image_path,
            destination_path,
            logdir=Path(DIRECTORIO_LOG)
        ) as img:
            # Procesar la imagen y optimizarla
            img.process_image()
            # 3.- extraer la información del QR
            # ahora, extraer el QR como imagen y el dato del QR en texto
            #    QR Code:
            data, qr_code = await img.extract_qr()
            print(data)

if __name__ == "__main__":
    asyncio.run(
        process_images(
            DIRECTORIO_ACTAS,
            DIRECTORIO_ACTAS_PROCESADAS,
            EXTENSION_ACTAS
        )
    )

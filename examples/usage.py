"""
Iterar sobre un directorio contentivo de Actas y procesarlas.
"""
import asyncio
from navconfig.conf import (
    DIRECTORIO_ACTAS,
    DIRECTORIO_ACTAS_PROCESADAS,
    EXTENSION_ACTAS,
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
    async for relative_path, destination_path, image_path in dir_iterator:
        # 1.- crear directorio (si no existe)
        dir_iterator.make_dir(destination_path)
        # 2.- Invocar al procesador de imágenes:
        img = ImageProcessor(image_path, destination_path)
        # 3.- extraer la información del QR


if __name__ == "__main__":
    asyncio.run(
        process_images(
            DIRECTORIO_ACTAS,
            DIRECTORIO_ACTAS_PROCESADAS,
            EXTENSION_ACTAS
        )
    )

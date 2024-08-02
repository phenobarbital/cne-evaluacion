"""
Image Processor.

Usado para post-procesar las actas electorales.
"""
from typing import Union
from collections.abc import Callable, Awaitable
import asyncio
from pathlib import PurePath, Path
import aiofiles
import cv2
from wand.image import Image
from wand.color import Color
import numpy as np
from navconfig import BASE_DIR
from navconfig.logging import logging

class ImageProcessor:
    """ImageProcessor.

    Class for Optimize and enhance Images.
    """
    logger: logging.Logger = None
    # pre-init and post-end functions
    pre_init: Awaitable[asyncio.Task] = None
    post_end: Awaitable[asyncio.Task] = None

    def __init__(
        self,
        image: Union[str, PurePath],
        destination_image: Union[str, PurePath],
        logdir: Union[None, PurePath] = None
    ) -> None:
        self.logger = logging.getLogger(
            "CNE.ImageProcessor"
        )
        self.image_file = image
        self.logger.debug(f"Processing Image: {image}")
        if isinstance(self.image_file, str):
            self.image_file = Path(image)
        self._destination = destination_image
        if isinstance(self._destination, str):
            self._destination = Path(self._destination)
        self._logdir = logdir
        if logdir is None:
            self._logdir = BASE_DIR.joinpath('Log')
        if self._logdir.exists() is False:
            self._logdir.mkdir(parents=True, exist_ok=True)
        self._log_handler = None
        self.log_file = self._logdir.joinpath('non_processed.log')

    async def __aenter__(self):
        self._log_handler = await aiofiles.open(self.log_file, mode='a')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._log_handler.close()

    async def log_error(self, error_message):
        """log_error.

        Saving Errors on Log File.
        """
        await self._log_handler.write(f"{error_message}\n")
        await self._log_handler.flush()

    def convert_to_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def adjust_contrast(self, image):
        # Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        return cv2.equalizeHist(image)

    def apply_noise_reduction(self, image):
        # Apply a gentle noise reduction
        return cv2.fastNlMeansDenoising(image, h=5)

    def apply_morphological_cleaning(self, image):
        # Apply morphological operations to clean up the image
        kernel = np.ones((3, 3), np.uint8)
        cleaned_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        cleaned_image = cv2.morphologyEx(cleaned_image, cv2.MORPH_CLOSE, kernel)
        return cleaned_image

    def apply_adaptive_sharpening(self, image):
        # Apply adaptive sharpening
        blurred = cv2.GaussianBlur(image, (0, 0), 3)
        sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
        return sharpened

    def sharpen_image(self, image):
        # Apply mild sharpening
        # kernel = np.array([[0, -0.3, 0], [-0.3, 2, -0.3], [0, -0.3, 0]])
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(image, -1, kernel)

    def unsharp_mask(self, image):
        # Apply unsharp masking
        blurred = cv2.GaussianBlur(image, (9, 9), 10.0)
        sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
        return sharpened

    def clean_black_dots(self, image):
        # Ensure the image is in color format before converting to grayscale
        if len(image.shape) == 2 or image.shape[2] == 1:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply binary thresholding
        _, binary_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        # Define a kernel for morphological operations
        kernel = np.ones((2, 2), np.uint8)

        # Apply morphological opening to remove small black dots
        cleaned_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

        # Apply morphological closing to enhance characters
        cleaned_image = cv2.morphologyEx(cleaned_image, cv2.MORPH_CLOSE, kernel)

        # Invert the image back to original form
        cleaned_image = cv2.bitwise_not(cleaned_image)

        return cleaned_image

    def crop_black_borders(self, image):
        # Ensure the image is in color format before converting to grayscale
        if len(image.shape) == 2 or image.shape[2] == 1:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply binary threshold
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

        # Find contours of the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get the bounding box of the largest contour that is significant
        significant_contour = None
        max_area = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area > max_area and area > (0.01 * image.shape[0] * image.shape[1]):  # Ignore very small contours
                max_area = area
                significant_contour = contour

        if significant_contour is not None:
            x, y, w, h = cv2.boundingRect(significant_contour)
            print(f"Bounding box: x={x}, y={y}, w={w}, h={h}")
            print(f"Image dimensions: width={image.shape[1]}, height={image.shape[0]}")

            # Check if the bounding box is significantly smaller than the image size
            if w < image.shape[1] * 0.95 and h < image.shape[0] * 0.95:
                cropped_image = image[y:y + h, x:x + w]
                return cropped_image

        # If no significant contour found or bounding box is too large, return original image
        return image

    def remove_noise_and_enhance(self, image):
        # Remove blue pixels (set them to white)
        lower_blue = np.array([100, 0, 0], dtype=np.uint8)
        upper_blue = np.array([255, 100, 100], dtype=np.uint8)
        mask = cv2.inRange(image, lower_blue, upper_blue)
        image[mask != 0] = [255, 255, 255]

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to convert to purely black and white
        _, binary_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Denoise the image
        denoised = cv2.fastNlMeansDenoising(binary_image, None, 30, 7, 21)

        # Sharpen the image
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(denoised, -1, kernel)

        return sharpened

    def enhance_image(self, image):
        # Convert to grayscale
        # gray = self.convert_to_grayscale(image)
        # Reduce noise
        # denoised = self.apply_noise_reduction(gray)
        # Clean up using morphological operations
        # cleaned_image = self.apply_morphological_cleaning(denoised)
        # Sharpen image
        sharpened = self.sharpen_image(image)
        # removing black areas on borders:
        final_image = self.crop_black_borders(sharpened)
        # final_image = self.clean_black_dots(cropped)
        return final_image

    def process_image(self, tolerance: float = 0.4):
        # 1. Read the image using OpenCV
        image = cv2.imread(self.image_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        # 2. Find the angle of the first horizontal line
        angle_degrees = 0
        for rho, theta in lines[:, 0]:
            if np.sin(theta) > 0.9:
                angle_degrees = np.degrees(theta) - 90
                break

        # 3. Always invert the angle to correct the rotation direction
        angle_degrees = -angle_degrees

        # 3. Rotate the image using Wand (ImageMagick) if needed
        print('Angle degrees: ', angle_degrees)
        if abs(angle_degrees) > tolerance:  # Tolerance of 0.4 degrees
            with Image(filename=self.image_file) as img:
                img.background_color = Color('white')  # Set white background
                img.rotate(angle_degrees, background=Color('white'))  # Rotate with white
                img.save(filename=self._destination)
                # Read the rotated image back into OpenCV
                rotated_image = cv2.imread(self._destination)
        else:
            # Read the image with no rotation
            rotated_image = cv2.imread(self.image_file)

        # 5. Enhance the image
        enhanced_image = self.enhance_image(rotated_image)

        # 6. Save the final image
        print(f'Saving final Image {self._destination}')
        if self._destination.parent.exists() is False:
            # create the directory first:
            self._destination.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(self._destination, enhanced_image)

    def remove_blue_artifacts(self, image):
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the range for blue color in HSV
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])

        # Create a mask for blue color
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Set the blue pixels to white
        image[mask != 0] = [255, 255, 255]

        return image

    async def extract_qr(self, area: float = 0.15):
        # Read the image
        directory = self._destination.parent
        # open the optimized image
        image = cv2.imread(self._destination)
        height, width = image.shape[:2]

        # Manually define the QR code region
        qr_height = int(height * area)  # 15% of the height
        qr_y_start = height - qr_height

        # Extract the QR code region
        qr_code_roi = image[qr_y_start:height, 0:width]

        # Remove blue artifacts
        cleaned_image = self.remove_blue_artifacts(qr_code_roi)

        # remove dots:
        no_dots = self.clean_black_dots(cleaned_image)
        # Convert to grayscale
        # gray = self.convert_to_grayscale(cleaned_image)

        # Apply a median blur to remove noise
        denoised = cv2.medianBlur(no_dots, 5)

        # Sharpen the image:
        sharpened = self.sharpen_image(denoised)

        # Initialize the QRCodeDetector
        qr_detector = cv2.QRCodeDetector()

        # Detect and decode the QR code
        decoded_info, points, _ = qr_detector.detectAndDecode(sharpened)
        if decoded_info:
            print(f"QR code decoded information: {decoded_info}")
            if points is not None:
                # Extract the bounding box coordinates
                points = points[0]
                x1, y1 = points[0]
                x2, y2 = points[2]

                # Convert coordinates to integer
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Extract the QR code region
                qr_code_roi = sharpened[y1:y2, x1:x2]

                # Save the QR code region
                output_path = Path(directory).joinpath(f"{self._destination.stem}_qr_code{self._destination.suffix}")
                cv2.imwrite(output_path, qr_code_roi)
                self.logger.debug(
                    f"QR code detected and saved to {output_path}"
                )
        else:
            self.logger.warning("No QR code detected")
            await self.log_error(str(self._destination))
        # Save the QR code region (bottom area:)
        output_path = Path(directory).joinpath(f"{self._destination.stem}_bottom{self._destination.suffix}")
        cv2.imwrite(output_path, sharpened)
        # saving data:
        if decoded_info:
            data_path = Path(directory).joinpath(f"{self._destination.stem}.txt")
            with open(data_path, "w+") as fp:
                fp.write(decoded_info)
                fp.flush()
        return decoded_info, output_path

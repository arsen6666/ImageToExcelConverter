import os

from dotenv import load_dotenv
from PIL import Image, ImageOps
import pytesseract
import pandas as pd
from flask_restx import Namespace, Resource, reqparse
import tempfile
import logging
from werkzeug.datastructures import FileStorage

load_dotenv()

convert_ns = Namespace('convert', description='Convert operations')

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

TEMP_IMAGE_DIR = os.getenv('TEMP_IMAGE_DIR')

logger = logging.getLogger(__name__)


@convert_ns.route('/image-to-excel')
@convert_ns.doc(description="Convert image to Excel")
class ImageToExcelResource(Resource):
    @convert_ns.expect(upload_parser)
    def post(self):
        try:
            args = upload_parser.parse_args()
            image_file = args.get('file')

            if not image_file.content_type.startswith('image/'):
                return {'error': 'Invalid Content-Type. Expected image file.'}, 400

            path = os.path.join(os.path.expanduser("~"), TEMP_IMAGE_DIR)

            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                os.makedirs(desktop_path)

            temp_image_path = os.path.join(path, image_file.filename)
            image_file.save(temp_image_path)

            image = Image.open(temp_image_path)
            image = ImageOps.grayscale(image)
            image = ImageOps.invert(image)
            image.save(temp_image_path)

            os.environ['LC_ALL'] = 'eng'
            text = pytesseract.image_to_string(image, config='--psm 6 --oem 3')

            text = ''.join(char for char in text if char.isalnum() or char.isspace())

            data = [line.split('\t') for line in text.split('\n')]
            df = pd.DataFrame(
                data, columns=[f'Column_{i}' for i in range(len(data[0]))]
            )

            temp_excel_fd, excel_file_path = tempfile.mkstemp(
                suffix='.xlsx', dir=path
            )
            os.close(temp_excel_fd)
            df.to_excel(excel_file_path, index=False)

            return {
                'message': 'Conversion successful',
                'excel_file_path': excel_file_path,
            }, 200

        except Exception as e:
            logger.exception(f"Error during conversion: {str(e)}")
            return {'error': f'Conversion failed. {str(e)}'}, 500

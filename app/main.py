from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from resources.convert_excel import convert_ns, ImageToExcelResource


def create_app():
    app = Flask(__name__)

    api = Api(
        app,
        version='1.0',
        title='Image to Excel API',
        description='API for converting images to Excel',
    )

    api.add_namespace(convert_ns)
    api.add_resource(ImageToExcelResource, '/convert/image-to-excel')

    CORS(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5555, debug=True)


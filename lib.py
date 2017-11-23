from openpyxl import load_workbook

from koala.ExcelCompiler import ExcelCompiler
from koala.ExcelError import ExcelError


def list_models():
    # TODO list the available models in S3
    return {}


def add_or_update_model(xlsx_file, model_id=None):
    # TODO serialise the xlsx_file and upload to S3, return the ID
    return {}


def get_model(model_id):
    # TODO get information about the serialised model and Excel file
    # e.g. inputs, outputs
    # maybe allow for optional level of detail to this?
    return {}


def delete_model(model_id):
    # TODO delete the serialised model and Excel file from S3
    return {}


def run_model(model_id, payload):
    # TODO get this working roughly following these steps
    #   - Get serialised model from S3
    #   - Load model with koala
    #   - Extract inputs from payload
    #   - Set the inputs in the model
    #   - Extract required outputs from payload (all outputs if none specifically requested)
    #   - Get the required outputs from the model
    #   - Build and return response
    return {}

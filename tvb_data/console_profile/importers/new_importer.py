
import numpy
from tvb.adapters.uploaders.abcuploader import ABCUploader
from tvb.basic.logger.builder import get_logger
from tvb.datatypes.time_series import TimeSeries



class FooDataImporter(ABCUploader):
    _ui_name = "Foo Data"
    _ui_subsection = "foo_data_importer"
    _ui_description = "Foo data import"
    logger = get_logger(__name__)

    def get_upload_input_tree(self):
        return [
            {'name': 'array_data',
             "type": "upload",
             #'type': "array", "quantifier": "manual",
             'required_type': '.npy',
             'label': 'please upload npy',
             'required': 'true'}
        ]

    def get_output(self):
        return [TimeSeries]

    def launch(self, array_data):

        array_data = numpy.loadtxt(array_data)

        ts = TimeSeries()
        ts.storage_path = self.storage_path
        #ts.configure()
        ts.write_data_slice(array_data)
        ts.close_file()
        return ts



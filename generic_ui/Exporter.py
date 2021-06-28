###################################################################################
#   Copyright (c) 2020-2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################

__author__ = "Romain LE DONGE"
__copyright__ = "Copyright (c) 2021 STMicroelectronics"
__license__ = """
    Copyright (c) 2020-2021 STMicroelectronics.
    All rights reserved.
    This software is licensed under terms that can be found in the LICENSE file in
    the root directory of this software component.
    If no LICENSE file comes with this software, it is provided AS-IS.
"""


from PySide2.QtCore import qDebug
from ai_logging.decoders import decoder
import numpy as np
import os
import time

class Exporter:
    EXPORT_TO_CSV = "CSV"
    EXPORT_TO_NUMPY_NPY = "Numpy (.npy)"
    EXPORT_TO_RAW = "Raw"

    def __init__(self, export_format, destination):
        self.export_format = export_format
        self.destination = destination


    def process(self, data_array):
        if len(data_array) <= 0:
            return 0

        decoder_to_use = decoder.get_decoder_for_data(data_array[0])

        data_sample = decoder_to_use.decode(data_array[0])
        if isinstance(data_sample, str):
            qDebug("Can't save text for now")
        elif isinstance(data_sample, np.ndarray):
            has_label = False if data_array[0].get('label',None) is None else True

            if len(data_sample.shape) == 1:
                self.processNumberData(data_array, data_sample.shape[0], has_label)
            elif len(data_sample.shape) == 2:
                self.processNumberData(data_array, data_sample.shape[0]*data_sample.shape[1], has_label)
            else:
                qDebug("Can't export data of dimensions > 2")
        else:
            qDebug("Error can't export this format")
            return -1


    def processNumberData(self, data_array, nb_cols, has_label=False):

        # TODO Export in files with folder as label or if image as image + label in another file
        # TODO No need for pandas just use numpy

        decoder_to_use = decoder.get_decoder_for_data(data_array[0])

        if self.export_format == self.EXPORT_TO_CSV:
            cols = ['data'+str(i+1) for i in range(nb_cols)]
            if has_label:
                cols.append('label')

            label_extension = ('-'+data_array[0].get('label')) if has_label else ''
            output_filename = os.path.join(self.destination, 'Capture-'+time.strftime("%Y-%m-%d-%Hh%Mm%Ss", time.localtime())+label_extension+'.csv')
            with open(output_filename, 'w') as f:
                line_to_write = ','.join(cols) + '\n'
                f.write(line_to_write)
                
                for data in data_array:
                    decoded_data = decoder_to_use.decode(data)
                    decoded_data = decoded_data.flatten()
                    if has_label:
                        line_to_write = ','.join([str(x) for x in decoded_data]) + ','+data.get('label')+'\n'
                    else:
                        line_to_write = ','.join([str(x) for x in decoded_data]) + '\n'
                    f.write(line_to_write)
                f.close()
                qDebug("Export to CSV has ended")
            
        elif self.export_format == self.EXPORT_TO_NUMPY_NPY:
            cols = ['data'+str(i+1) for i in range(nb_cols)]
            labels = []
            if has_label:
                for data in data_array:
                    labels.append(data.get('label'))
                labels = list(set(labels))
            
            if len(labels) == 0: # Simple export all data to a single file
                all_data = []
                for data in data_array:
                    decoded_data = decoder_to_use.decode(data)
                    all_data.append(decoded_data)
                all_data = np.array(all_data)
                output_filename = os.path.join(self.destination, 'Capture-'+time.strftime("%Y-%m-%d-%Hh%Mm%Ss", time.localtime())+'.npy')
                np.save(output_filename, all_data)
            else: # Export to multiple file with label as filename
                all_data = {}
                for l in labels: # Preparing output dict
                    all_data[l] = []

                for data in data_array:
                    decoded_data = decoder_to_use.decode(data)
                    all_data[data.get('label')].append(decoded_data)

                for k in all_data.keys():
                    output_filename = os.path.join(self.destination, 'Capture-'+time.strftime("%Y-%m-%d-%Hh%Mm%Ss", time.localtime())+'-'+k+'.npy')
                    np.save(output_filename, np.array(all_data[k]))
            qDebug("Export to NPY has ended")


        elif self.export_format == self.EXPORT_TO_RAW:
            import pickle
            output_filename = os.path.join(self.destination, 'RawCapture-'+time.strftime("%Y-%m-%d-%Hh%Mm%Ss", time.localtime())+'.pkl')
            with open(output_filename, 'wb') as f:
                pickle.dump(data_array, f)
                f.close()

        else:
            qDebug("Error unknown format {}".format(self.export_format))
            return -1
        

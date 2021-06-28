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


# Use Semantic Versioning, http://semver.org/
version_info = (0, 4, 2)
__version__ = '%d.%d.%d' % version_info

from .core import *
from .drivers import *
from .decoders import *
#from .gui import *
from .core.ai_logging_api_wrapper import AILoggingPayloadType as types
from .decoders.decoder import get_decoder_for_data
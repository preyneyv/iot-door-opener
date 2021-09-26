import logging
from .helpers import data_path

logging.basicConfig(filename=data_path('access_log.txt'),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger('IoTDoorOpener')

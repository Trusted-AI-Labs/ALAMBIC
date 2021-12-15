# All the part of a text such as sentence, word, etc.
# Inspired by https://github.com/machinalis/iepy/
# Using the amazing Stanza library : https://github.com/stanfordnlp/stanza

from stanza.server import CoreNLPClient, StartServer

from alambic_app.models.input_models import Text
from alambic_app.constantes import ENDPOINT_CORENLP


def initialize_client(properties):
    """
    Create the CoreNLPClient
    :param properties: dictionry of the options chosen by the user for the text processing
    :return: stanza.server.CoreNLPClient
    """
    client = CoreNLPClient(properties=properties, endpoint=ENDPOINT_CORENLP)
    return client

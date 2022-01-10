# All the part of a text such as sentence, word, etc.
# Inspired by https://github.com/machinalis/iepy/
# Using the amazing Stanza library : https://github.com/stanfordnlp/stanza

from stanza.server import CoreNLPClient, StartServer

from alambic_app.models.input_models import Text
from alambic_app.constantes import ENDPOINT_CORENLP


def initialize_client(annotators):
    """
    Create the CoreNLPClient
    :param properties: dictionry of the options chosen by the user for the text processing
    :return: stanza.server.CoreNLPClient
    """
    properties = dict()
    if 'coref' in annotators:
        properties['coref.algorithm'] = "neural"
    client = CoreNLPClient(
        annotators=annotators,
        output_format="json",
        properties=properties,
        endpoint=ENDPOINT_CORENLP,
        start_server=StartServer.DONT_START
    )
    return client

# TODO : embedding, bow, tf-idf

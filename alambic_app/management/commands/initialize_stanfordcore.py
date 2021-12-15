from django.core.management.base import BaseCommand

import stanza


# add here the new tables as they are built

class Command(BaseCommand):
    args = 'None'
    help = 'Install Stanford Core NLP'

    def handle(self, *args, **options):
        stanza.install_corenlp()

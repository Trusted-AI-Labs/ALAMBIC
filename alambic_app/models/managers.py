import logging

from django.db.models import Manager

from input_models import *


class DataManager(Data):

    def import_data(self, file):
        """
        Import the data from the file into Data model instances in the db
        :param file: str, filename
        :return: None
        """
        with open(file, encoding='utf-8') as infile:
            data = infile.readlines()

        if '.tsv' in file:
            sep = '\t'
        else:
            sep = ','

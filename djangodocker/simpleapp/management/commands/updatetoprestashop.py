from django.core.management.base import BaseCommand, CommandError
from djangodocker.simpleapp.prestashop import ControllerPrestashop
from djangodocker.simpleapp.controller import ControllerICGProducts
import logging
from datetime import datetime

class Command(BaseCommand):
    help = 'Update all objects with "updated" flag to Prestashop'

    def handle(self, *args, **options):
        logger = logging.getLogger('command.updatetoprestashop')
        c = ControllerICGProducts()
        updated, result = c.updateDataFromICG()
        if updated:
            logger.info("[" + str(datetime.now()) + "] Objects updated from ICG " + str(result))

        p = ControllerPrestashop()
        updated, result = p.carregaNous()
        if updated:
            logger.info("[" + str(datetime.now()) + "] Objects updated to PS " +  str(result))
        #logger.info("UpdateToPS ended")
        #TODO: In try and if except, send email

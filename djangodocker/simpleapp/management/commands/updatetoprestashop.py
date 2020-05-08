from django.core.management.base import BaseCommand, CommandError
from djangodocker.simpleapp.prestashop import ControllerPrestashop
from djangodocker.simpleapp.controller import ControllerICGProducts
import logging

class Command(BaseCommand):
    help = 'Update all objects with "updated" flag to Prestashop'

    def handle(self, *args, **options):
        logger = logging.getLogger('command.updatetoprestashop')
        c = ControllerICGProducts()
        result = c.updateDataFromICG()
        logger.info('Objects updated from ICG %s' % str(result))
        p = ControllerPrestashop()
        result = p.carregaNous()
        logger.info('Objects updated to PS %s' % str(result))

from django.core.management.base import BaseCommand, CommandError
from djangodocker.simpleapp.prestashop import ControllerPrestashop
from djangodocker.simpleapp.controller import ControllerICGProducts
import logging
from datetime import datetime
from filelock import FileLock, Timeout


class Command(BaseCommand):
    help = 'Get new things from MSSQL Server'

    def add_arguments(self, parser):
        parser.add_argument("tipus", type=str)

    def handle(self, *args, **options):
        logger = logging.getLogger('command.directeicg')

        try:
            lock = FileLock("directeicg.lock", timeout=10)
            with lock.acquire(timeout=10):
                tipus = options['tipus']
                c = ControllerICGProducts()
                if tipus == "product":
                    c.saveNewProductsDirecte()
                elif tipus == "price":
                    c.saveNewPricesDirecte()
                elif tipus == "stock":
                    c.saveNewStocksDirecte()
                else:
                    raise Exception("Comanda no trobada")

        except Timeout:
            logger.info("[" + str(datetime.now()) + "] Directe ICG is blocked!")


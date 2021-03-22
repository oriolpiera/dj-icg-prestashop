from django.core.management.base import BaseCommand, CommandError
from djangodocker.simpleapp.prestashop import ControllerPrestashop
from djangodocker.simpleapp.controller import ControllerICGProducts
import logging
from datetime import datetime
from filelock import FileLock, Timeout


class Command(BaseCommand):
    help = 'Update all objects with "updated" flag to Prestashop'
    #lock = False

    def handle(self, *args, **options):
        logger = logging.getLogger('command.updatetoprestashop')

        #if self.lock:
        #    logger.info("[" + str(datetime.now()) + "] UpdateFromPrestashop is blocked!")
        #    return True
        #self.lock=True
        try:
            lock = FileLock("update_from_icg.lock", timeout=10)
            with lock.acquire(timeout=10):
                c = ControllerICGProducts()
                updated, result = c.updateDataFromICG()
                if updated:
                    logger.info("[" + str(datetime.now()) + "] Objects updated from ICG " + str(result))

                p = ControllerPrestashop()
                updated, result = p.carregaNous()
                if updated:
                    logger.info("[" + str(datetime.now()) + "] Objects updated to PS " +  str(result))
                if len(result['errors']) > 0:
                    logger.error("[" + str(datetime.now()) + "] Objects with error " + str(result['errors']))
        except Timeout:
            logger.info("[" + str(datetime.now()) + "] UpdateFromPrestashop is blocked!")
        #self.lock=False
        #logger.info("[" + str(datetime.now()) + "] UpdateToPS ended")
        #TODO: In try and if except, send email

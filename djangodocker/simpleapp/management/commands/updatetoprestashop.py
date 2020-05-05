from django.core.management.base import BaseCommand, CommandError
from djangodocker.simpleapp.prestashop import ControllerPrestashop

class Command(BaseCommand):
    help = 'Update all objects with "updated" flag to Prestashop'

    def handle(self, *args, **options):
        c = ControllerPrestashop()
        result = c.carregaNous()
        self.stdout.write(self.style.SUCCESS('Objects updated %s' % str(result)))

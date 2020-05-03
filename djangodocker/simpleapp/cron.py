from django_cron import CronJobBase, Schedule
from . import models, mssql, controller, prestashop, mytools, constants

class ProductCronJob(CronJobBase):
    RUN_EVERY_MINS = ['09:10']

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'simpleapp.product_icg_cron'    # a unique code

    def do(self):
        c = controller.ControllerICGProducts()
        c.saveNewProducts(constants.URLBASE)
        pass    # do your thing here

class PriceCronJob(CronJobBase):
    RUN_EVERY_MINS = ['09:20']

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'simpleapp.price_icg_cron'    # a unique code

    def do(self):
        c = controller.ControllerICGProducts()
        c.saveNewPrices(constants.URLBASE)
        pass    # do your thing here

class StockCronJob(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'simpleapp.stock_icg_cron'    # a unique code

    def do(self):
        c = controller.ControllerICGProducts()
        c.saveNewStocks(constants.URLBASE)
        pass    # do your thing here

# vim: et ts=4 sw=4

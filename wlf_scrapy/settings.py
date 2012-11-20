# Wonderland Forum Scraping Bot made by tyteen4a03
# All rights reserved.

BOT_NAME = 'wlf_scrapy'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['wlf_scrapy.spiders']
NEWSPIDER_MODULE = 'wlf_scrapy.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)


# Scrapy settings for gpbscraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# Or you can copy and paste them from where they're defined in Scrapy:
# 
#     scrapy/conf/default_settings.py
#

import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gpbweb')))


BOT_NAME = 'gpbscraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['gpbscraper.spiders']
NEWSPIDER_MODULE = 'gpbscraper.spiders'
DEFAULT_ITEM_CLASS = 'gpbscraper.items.CompraItem'
#USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-US) AppleWebKit/534.2 (KHTML, like Gecko) Chrome/6.0.453.1 Safari/534.2'

#ITEM_PIPELINES = ['gpbscraper.pipelines.ItemCounterPipeline', 'gpbscraper.pipelines.ComprasPersisterPipeline']
#ITEM_PIPELINES = ['gpbscraper.pipelines.ProveedoresPersisterPipeline']#, 'gpbscraper.pipelines.CompraLineasPersisterPipeline']
ITEM_PIPELINES = ['gpbscraper.pipelines.CompraLineasPersisterPipeline']
#ITEM_PIPELINES = []

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gpbweb.settings')

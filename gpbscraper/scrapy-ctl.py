#!/usr/bin/env python

import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'gpbscraper.settings')

from scrapy.cmdline import execute
execute()

# Wonderland Forum Scraping Bot made by tyteen4a03
# All rights reserved.

import re

def br2nl(string):
    return re.sub("<br[^>]*>", "\n", string)
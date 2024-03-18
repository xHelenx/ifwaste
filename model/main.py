# IF-WASTE Version 1a
#  Additions from GAK
#   Uncommented time and income in House object to limit food purchases and cooking activities
#   Deducted total Price of food from House budget
 
import logging
from Neighborhood import Neighborhood
logging.getLogger(__name__)
logging.basicConfig(filename="debug.log",encoding="utf-8",level=logging.DEBUG, filemode="w")
        
neighborhood = Neighborhood(num_houses=1)
neighborhood.run(days=5)
#neighborhood.data_to_csv()
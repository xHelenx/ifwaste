# IF-WASTE Version 1a
#  Additions from GAK
#   Uncommented time and income in House object to limit food purchases and cooking activities
#   Deducted total Price of food from House budget
 
from Neighborhood import Neighborhood

neighborhood = Neighborhood(num_houses=1)
neighborhood.run(days=10)
neighborhood.data_to_csv()
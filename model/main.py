import logging
from Neighborhood import Neighborhood
from House import House


#setup logging -> logging file is generated as "debug.log" in ifwaste folder
logging.getLogger(__name__)
logging.basicConfig(filename="debug.log",encoding="utf-8",level=logging.DEBUG, filemode="w")

#configure houses
h0 = House(id=0,is_serving_based=True)
h1 = House(id=1,is_serving_based=True)
h2 = House(id=2,is_serving_based=False)
h3 = House(id=3,is_serving_based=False)
  
#setup neighborhood  
neighborhood = Neighborhood(houses=[h0,h1,h2,h3])
#neighborhood = Neighborhood(houses=[h0])

#run simulation
neighborhood.run(days=100)

#collect data
neighborhood.data_to_csv()
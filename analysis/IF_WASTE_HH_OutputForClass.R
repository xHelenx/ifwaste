library(tidyverse)
library(ggplot2)
library(gridExtra)
library(cowplot)
library(ineq)
library(gglorenz)
library(hrbrthemes)


#STUDENTS Set the paths to whereever you are working... remember to change your \ to /  

hh_foodwasted <- read.csv("E:/UF/ifwaste/data/2024-03-21at11-44/wasted.csv")
hh_foodeaten <- read.csv("E:/UF/ifwaste/data/2024-03-21at11-44/eaten.csv")
hh_foodremaining <- read.csv("E:/UF/ifwaste/data/2024-03-21at11-44/still_have.csv")
hh_foodbought <- read.csv("E:/UF/ifwaste/data/2024-03-21at11-44/bought.csv")


#ggplot(hh_foodwasted,aes(x=Type,y=kg,group=House)) + geom_boxplot()+ggtitle("Wasted Food") + ylab("Kg Wasted")+ xlab("Food Category")+ theme(axis.text.x=element_text(angle = 45, vjust = 1, hjust=1 ))
#ggplot(hh_foodbought,aes(x=Day.Bought,y=Price,group=House)) + geom_boxplot()+ggtitle("Food Bought") + ylab("Price")+ xlab("Time")+theme_bw()


#Energy Rainbow Graphs
fnvbought <- dplyr::filter(hh_foodbought,Type=="Fruits & Vegetables")

hh0wasted_only<- dplyr::filter(hh_foodwasted,House==0)
hh1wasted_only<- dplyr::filter(hh_foodwasted,House==1)
hh2wasted_only<- dplyr::filter(hh_foodwasted,House==2)
hh3wasted_only<- dplyr::filter(hh_foodwasted,House==3)
hh4wasted_only<- dplyr::filter(hh_foodwasted,House==4)
hh5wasted_only<- dplyr::filter(hh_foodwasted,House==5)
hh6wasted_only<- dplyr::filter(hh_foodwasted,House==6)

hh0eaten_only<- dplyr::filter(hh_foodeaten,House==0)
hh1eaten_only<- dplyr::filter(hh_foodeaten,House==1)
hh2eaten_only<- dplyr::filter(hh_foodeaten,House==2)
hh3eaten_only<- dplyr::filter(hh_foodeaten,House==3)
hh4eaten_only<- dplyr::filter(hh_foodeaten,House==4)
hh5eaten_only<- dplyr::filter(hh_foodeaten,House==5)
hh6eaten_only<- dplyr::filter(hh_foodeaten,House==6)

hh0remain_only<- dplyr::filter(hh_foodremaining,House==0)
hh1remain_only<- dplyr::filter(hh_foodremaining,House==1)
hh2remain_only<- dplyr::filter(hh_foodremaining,House==2)
hh3remain_only<- dplyr::filter(hh_foodremaining,House==3)
hh4remain_only<- dplyr::filter(hh_foodremaining,House==4)
hh5remain_only<- dplyr::filter(hh_foodremaining,House==5)
hh6remain_only<- dplyr::filter(hh_foodremaining,House==6)

hh0bought_only<- dplyr::filter(hh_foodbought,House==0)
hh1bought_only<- dplyr::filter(hh_foodbought,House==1)
hh2bought_only<- dplyr::filter(hh_foodbought,House==2)
hh3bought_only<- dplyr::filter(hh_foodbought,House==3)
hh4bought_only<- dplyr::filter(hh_foodbought,House==4)
hh5bought_only<- dplyr::filter(hh_foodbought,House==5)
hh6bought_only<- dplyr::filter(hh_foodbought,House==6)



ggplot()+ggtitle("Fruits & Veg") +
geom_line(data=fnvbought,aes(x=Day.Bought,y=Price,group=House,colour = House), alpha = 0.4, size = 2)
+ geom_line()+labs(y= "Fruits&Veg Bought (kg)", x = "Month") + scale_color_gradientn(colours = rainbow(20))+ ylim(0, 25)


#Stacked Bar

fill <- c("darkgrey","tan2","forestgreen","red","yellow","purple","cyan")
leglabels <- c("Dairy & Eggs", "Dry Foods & Baked Goods","Fruits & Vegetables","Meat& Fish",
               "Snacks, Condiments, Liquids, Oils, Grease, & Other","Store-Prepared Items","Cooked, Prepped, Leftovers")

fill_wasted <- c("darkgrey","purple","pink","cyan")
leglabels_wasted <- c("Inedible","Store-Prepped","Home-Prepped, Un-Prepped")


hh0_buy <- ggplot()+ggtitle("HH #0 Food Kg Purchased")+labs(y= "Food Purchased (kg)", x = "Simuated Days") 
    + geom_bar(aes(y = kg, x = Day.Bought, fill = Type), data = hh0bought_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh0_buy

hh0_wasted <- ggplot()+ggtitle("HH #0 Food Kg Wasted")+labs(y= "Food Wasted (kg)", x = "Simuated Days") 
+ geom_bar(aes(y = kg, x = Day.Wasted, fill = Type), data = hh0wasted_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh0_wasted

hh0_wasted_cost <- ggplot()+ggtitle("HH #0 Food $ Wasted")+labs(y= "Food Wasted ($)", x = "Simuated Days")
 + geom_bar(aes(y = Price, x = Day.Wasted, fill = Type), data = hh0wasted_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh0_wasted_cost


hh0_wasted_status <- ggplot()+ggtitle("HH #0 Food Kg Wasted")+labs(y= "Food Wasted (kg)", x = "Simuated Days")
 + geom_bar(aes(y = kg, x = Day.Wasted, fill = Status), data = hh0wasted_only, stat="identity") +
  scale_fill_manual(values = fill_wasted)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh0_wasted_status




hh1_buy <- ggplot()+ggtitle("HH #1 Food Kg Purchased")+labs(y= "Food Purchased (kg)", x = "Simuated Days") 
+ geom_bar(aes(y = kg, x = Day.Bought, fill = Type), data = hh1bought_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh1_buy

hh1_wasted <- ggplot()+ggtitle("HH #1 Food Kg Wasted")+labs(y= "Food Wasted (kg)", x = "Simuated Days") 
+ geom_bar(aes(y = kg, x = Day.Wasted, fill = Type), data = hh1wasted_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh1_wasted

hh1_wasted_cost <- ggplot()+ggtitle("HH #1 Food $ Wasted")+labs(y= "Food Wasted ($)", x = "Simuated Days") 
+ geom_bar(aes(y = Price, x = Day.Wasted, fill = Type), data = hh1wasted_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh1_wasted_cost


hh1_wasted_status <- ggplot()+ggtitle("HH #1 Food Kg Wasted")+labs(y= "Food Wasted (kg)", x = "Simuated Days") 
+ geom_bar(aes(y = kg, x = Day.Wasted, fill = Status), data = hh1wasted_only, stat="identity") +
  scale_fill_manual(values = fill_wasted)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh1_wasted_status




hh2_buy <- ggplot()+ggtitle("HH #2 Food Kg Purchased")+labs(y= "Food Purchased (kg)", x = "Simuated Days") 
+ geom_bar(aes(y = kg, x = Day.Bought, fill = Type), data = hh2bought_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh2_buy

hh3_buy <- ggplot()+ggtitle("HH #3 Food Kg Purchased")+labs(y= "Food Purchased (kg)", x = "Simuated Days") 
+ geom_bar(aes(y = kg, x = Day.Bought, fill = Type), data = hh3bought_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh3_buy

hh4_buy <- ggplot()+ggtitle("HH #4 Food Kg Purchased")+labs(y= "Food Purchased (kg)", x = "Simuated Days")
 + geom_bar(aes(y = kg, x = Day.Bought, fill = Type), data = hh4bought_only, stat="identity") +
  scale_fill_manual(values = fill)  + 
  theme(legend.position = c(0.72, 0.85),
        legend.key.size = unit(1, 'mm'), #change legend key size
        legend.key.height = unit(1, 'mm'), #change legend key height
        legend.key.width = unit(1, 'mm'), #change legend key width
        legend.title = element_text(size=10), #change legend title font size
        legend.text = element_text(size=6)) #change legend text font size)+ theme_bw()
hh4_buy

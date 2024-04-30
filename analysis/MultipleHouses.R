
# Loading necessary libraries
# Install packages if you haven't already 
install.packages("ggplot2")
install.packages("patchwork")

library(ggplot2)
library(patchwork)

# Read the CSV file
data <- read.csv("E:/UF/ifwaste/data/2024-03-21at14-38/wasted.csv")

# Assuming your data frame has columns 'House', 'DayWasted', and 'KgWasted'
# Convert House to a factor if it's not already
data$House <- as.factor(data$House)

# Create a list to store plots
plots_list <- list()

# Looping through each house and creating a plot for each
for(house in unique(data$House)) {
  house_data <- subset(data, House == house)
  p <- ggplot(house_data, aes(x = Day.Wasted, y = kg)) +
    geom_line() + # Use geom_line() for line plots
    geom_point() + # Add points on each data point
    ggtitle(paste("House", house)) +
    xlab("Day Wasted") +
    ylab("Kg Wasted")
  plots_list[[as.character(house)]] <- p
}


# To combine all plots in plots_list into one plot
plot_layout <- wrap_plots(plots_list)

# specify the layout explicitly, for example, in a 2x5 grid
plot_layout <- wrap_plots(plots_list, ncol = 2)

# Combining the plots.Layouts can be adjusted here
#plot_layout <- reduce(plots_list, `+`)
#plot_layout + plot_layout_guides(ncol = 2)

print(plot_layout)

library(RODBC)
library(plyr)
library(hydroGOF)

# CHANGE THESE ###########
# SWAT project
projectDir = "H:/WRB"
# Subbasin ID
#   from Marathon County
subbasinID = 262
# Raw USGS data
obsDataFile = "T:/Projects/Wisconsin_River/GIS_Datasets/observed/Avg_cornGrainYlds_byCounty.csv"
monthly = T
run = "default crop parameters"
# DON'T CHANGE ANYTHING BELOW HERE #####

cornGrain <- read.csv(obsDataFile)
cornGrain$DATE <- as.Date(as.character(paste(cornGrain[,1],9,1,sep ='-')))
# to convert from bu/acre to Mg/ha
cornGrain$OBSERVED_YLDbu_acre <- cornGrain$Value..BU.ACRE. #*  .0628
obsData <- cornGrain[cornGrain$County == 'MARATHON',]

# for modeled data
outDb = paste(projectDir, "Scenarios/Default/TablesOut/SWATOutput.mdb", sep="/")
con = odbcConnectAccess(outDb)

query = paste("SELECT YEAR, MON, LULC, BIOMt_ha, YLDt_ha FROM hru WHERE SUB =", subbasinID)

modData = sqlQuery(con, query)
close(con)

#grabbing just corn
modData <- modData[modData$LULC == 'CORN',]
modData <- modData[modData$MON == 9,]

# formating time series
mon = formatC(modData$MON, width = 2, format = "d", flag = "0")
modTS = as.Date(paste(modData$YEAR, mon, "01", sep="-"))                                          
modData = data.frame("DATE" = modTS, 
                     MODELED_YLDbu_acre = (modData$YLDt_ha)*(15.92357))

modData <- aggregate(modData$MODELED_YLDbu_acre, list(modData$DATE), mean)
names(modData) <- c('DATE', 'MODELED_YLDbu_acre')
#modData <- modData[modData$DATE,]
plot(MODELED_YLDbu_acre ~ DATE, data = modData, type = 'l', ylim = c(20, 200))
lines(OBSERVED_YLDbu_acre ~ DATE, data = obsData, type = 'l', col = 'red')

plotDir = paste(projectDir, "plots", sep="/")

if (!file.exists(plotDir)) {
    dir.create(plotDir)
}
d = merge(obsData, modData)
pbs <- paste('Percent bias:', pbias(d$MODELED_YLDbu_acre, d$OBSERVED_YLDbu_acre))

pdf(paste(plotDir, "/", run, ".pdf", sep=""), width=11, height=8.5)

ylim = c(20, 250)
plot(OBSERVED_YLDbu_acre ~ DATE,
    data=d,
	type="l",
	col="aquamarine",
	ylab="Avg Yield bu/acre",
	xlab="Date",
	ylim=ylim,
	lwd=3)
lines(MODELED_YLDbu_acre ~ DATE, data=d, col="coral1", lwd=3)
title(paste('Subbasin', subbasinID, 'Corn Yield'))
legend("topright", c("Modeled", "Observed", pbs), fill=c("coral1","aquamarine", 'white'))
#text(as.Date(2004-01-01), 230, labels = paste("Percent Bias =",pbs ))
dev.off()

plot(Value..BU.ACRE. ~ Date, data = marathon, type = 'l')

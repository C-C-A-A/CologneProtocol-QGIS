##Cologne-Protocol=group
##showplots
##Layer=vector LEC
##Feld=Field Layer HubDist
##model=selection Exp;Sph;Gau;Mat 1
##LagDist = number
##Plot.Show.First.X.Percent = number 50
##Use_ggplot2_for_Plotting=boolean True
## out.range = output number
## out.psill = output number
## out.nugget = output number
##Variogram_Results=Output table


# Turn Scientific notation off
options(scipen=999)
library(gstat)

lzn.vgm <- gstat::variogram((Layer[[Feld]])~1, Layer,width=LagDist)

d1 <-diff(lzn.vgm$gamma)
which.max((d1 / d1[1]) < 0.1)  
range.plateau <- lzn.vgm$dist[which.max((d1 / d1[1]) < 0.1)]
sill.plateau <- lzn.vgm$gamma[lzn.vgm$dist == range.plateau]

# Fit Model
Models<-c("Exp","Sph","Gau","Mat")
model2<-Models[model+1]


  
lzn.fit <- fit.variogram(lzn.vgm, model=vgm(sill.plateau,model2, range.plateau, nugget=0), fit.sills = FALSE, fit.ranges = FALSE)


out.nugget <- round(lzn.fit$psill[1])
out.range <- round(lzn.fit$range[2])
out.psill <- round(lzn.fit$psill[2])

exp <- paste(out.nugget, "+",out.psill,"*x+",out.range,"*x*x",sep="")
pwr <- paste(out.nugget, "+",out.psill,"*x^",out.range,sep="")
sph <- paste(out.nugget, "+", out.psill, "* ifelse(x >",out.range,", 1, 1.5 * x / ",out.range," - 0.5 * x*x*x / ",out.range,"*",out.range,"*",out.range,sep="")

# Plot Sample Variogramm and fitted Modell
xlim.value = ((max(lzn.vgm$dist)/100)*Plot.Show.First.X.Percent)
ylim.value = ((max(lzn.vgm$gamma)/100)*Plot.Show.First.X.Percent)
titel <- paste(lzn.fit$model[2]," model, 1. Plateau range = ",as.character(round(range.plateau,0)), ", psill = ", out.psill, sep="")
plot(lzn.vgm, lzn.fit, main=titel, xlim=c(0, xlim.value), ylim=c(0, ylim.value))
#abline(v=range.plateau)
#segments(x0 = out.range, y0 = 0, x1 = out.range, y1 = max(lzn.vgm$gamma), lwd = 2)

if(Use_ggplot2_for_Plotting){ 
library(ggplot2)
library(gridExtra)

vgm.line <- variogramLine(lzn.fit, maxdist = max(lzn.vgm$dist))
p1 <- ggplot(lzn.vgm, aes(x = dist, y = gamma)) + geom_line(data = vgm.line) + geom_point() + geom_vline(xintercept = range.plateau,col="red") +
  xlim(0, xlim.value) +  ylim(0, ylim.value) + ggtitle(titel) +
  xlab("Distance") + ylab("Semivariance") 
p2 <- ggplot(lzn.vgm, aes(x = dist, y = gamma)) + geom_line(data = vgm.line) + geom_point() + geom_vline(xintercept = range.plateau,col="red") +
  ggtitle(titel) +
  xlab("Distance") + ylab("Semivariance") 

grid.arrange(p1,p2,nrow=2)
}

# Export results
Variogram_Results <- data.frame("Model" = lzn.fit$model[2], "Nugget" = out.nugget, "Range" = round(out.range,0), "Psill" = round(out.psill,0), "exp" = exp, "pwr" = pwr, "sph" = sph)

# Print Results
>print("")
>print("")
>print("*********************************************************************")
>print("")
>print("RESULTS:")
>print("")
>lzn.fit
>print("")
>paste("model = ", lzn.fit$model[2], sep="")
>paste("nugget = ",out.nugget,sep="")
>paste("psill = ",out.psill,sep="")
>paste("range = ", out.range, sep="")
>print("")
>print("Exponential Model:")
>print(exp)
>print("Power Model:")
>print(pwr)
>print("Spherical Model:")
>print(sph)
>print("")
>print("***DONE***")
>print("")

# Step 7: Semivariogram

# Initalzing input parameters

##Cologne-Protocol=group
##showplots
##Layer=vector LEC
##Field=Field Layer HubDist
##model=selection Exp;Sph 0
##LagDist = number (Bounding Geometry[[LagDist]])
##Plot.Show.First.X.Percent = number 50
##Use_ggplot2_for_Plotting=boolean True
## out.range = output number
## out.psill = output number
## out.nugget = output number
##Variogram_Results=Output table


# Turn Scientific notation off
options(scipen=999)
library(gstat)


# Build Sample variogram
lzn.vgm <- gstat::variogram((Layer[[Field]])~1, Layer,width=LagDist)


# Identify first plateau for fitting theoretical variogram 
d1 <-diff(lzn.vgm$gamma)
which.max((d1 / d1[1]) < 0.1)  
range.plateau <- lzn.vgm$dist[which.max((d1 / d1[1]) < 0.1)]
sill.plateau <- lzn.vgm$gamma[lzn.vgm$dist == range.plateau]


# Fitting theoretical variogram
Models<-c("Exp","Sph")
model2<-Models[model+1] 
lzn.fit <- fit.variogram(lzn.vgm, model=vgm(sill.plateau,model2, range.plateau, nugget=0), fit.sills = FALSE, fit.ranges = FALSE)


# Defining outputs: nugget, range, psill
out.nugget <- round(lzn.fit$psill[1])
out.range <- round(lzn.fit$range[2])
out.psill <- round(lzn.fit$psill[2])


# Defining outputs: formulas/models
exp <- paste(out.nugget, "+",out.psill,"*x+",out.range,"*x*x",sep="")
pwr <- paste(out.nugget, "+",out.psill,"*x**",out.range,sep="")
sph <- paste(out.nugget, "+", out.psill, "* ifelse(x >",out.range,", 1, 1.5 * x / ",out.range," - 0.5 * x*x*x / ",out.range,"*",out.range,"*",out.range,sep="")

out.formula <- ""
if (lzn.fit$model[2]=="Sph"){out.formula <- sph}
if (lzn.fit$model[2]=="Exp"){out.formula <- exp}

# Plot Sample Variogramm and fitted Model using basic plotting:
xlim.value = ((max(lzn.vgm$dist)/100)*Plot.Show.First.X.Percent)
ylim.value = ((max(lzn.vgm$gamma)/100)*Plot.Show.First.X.Percent)
titel <- paste(lzn.fit$model[2]," model, 1. Plateau range = ",as.character(round(range.plateau,0)), ", psill = ", out.psill, sep="")
plot(lzn.vgm, lzn.fit, main=titel, xlim=c(0, xlim.value), ylim=c(0, ylim.value))

# Plot Sample Variogramm and fitted Model using ggplot2:
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

# Export results as table
Variogram_Results <- data.frame("Model" = lzn.fit$model[2], "Nugget" = out.nugget, "Range" = round(out.range,0), "Psill" = round(out.psill,0), "Choosen_Model" = out.formula, "exp" = exp, "pwr" = pwr, "sph" = sph)


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

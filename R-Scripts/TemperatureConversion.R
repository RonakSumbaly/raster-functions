require(raster)
temperatureConversion <- function(r,par,noData){
  ras <- raster(r)
  if (par==0)
  {
    values(ras) = values(ras) * 9.0/5.0 + 32.0
  }
  else
  {
    values(ras) = (values(ras) - 32.0) * 5.0/9.0
  } 
  return (values(ras))
}

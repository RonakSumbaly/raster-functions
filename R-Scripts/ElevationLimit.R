require(raster)
elevationLimit <- function(r,par,noData){
  ras = raster(r)
  values(ras) <- ifelse(values(ras)<par,noData,values(ras))
  return (values(ras))
}

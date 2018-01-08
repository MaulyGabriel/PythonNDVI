import gdal
from gdal import Open
from ndvi import ndvi


# Abrindo banda NIR
nir_tiff = Open(r'NIR_IMAGE.tif')
#nir_tiff = Open(r'nir.tif')
nir_band = nir_tiff.GetRasterBand(1)

# Abrindo banda RED.
red_tiff = Open(r'RED_IMAGE.tif')
#red_tiff = Open(r'red.tif') 
red_band = red_tiff.GetRasterBand(1)

# Get the rows and cols from one of the images (both should always be the same)
rows, cols, geotransform = nir_tiff.RasterYSize, nir_tiff.RasterXSize, nir_tiff.GetGeoTransform()
print(geotransform)

# Arquivo de saida 16-bit (0-255)
out_tiff_int16 = r'NDVI_16.tif'

# Arquivo de saida 32-bit floating point (-1 to 1)
out_tiff_float32 = r'NDVI_32.tif'

# Gerando imagem  NDVI 16-bit integer
ndvi(nir_band, red_band, rows, cols, geotransform, out_tiff_int16, gdal.GDT_UInt16)

# Gerando imagem NDVI 32-bit floating point
ndvi(nir_band, red_band, rows, cols, geotransform, out_tiff_float32, gdal.GDT_Float32)

print('done')
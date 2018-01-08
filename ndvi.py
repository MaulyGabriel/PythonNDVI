import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.colors as colors 
from numpy import nan_to_num, subtract, add, divide, multiply
from osgeo import gdal, gdalconst
from gdal import GetDriverByName
from highcharts import Highchart


#inicializando o graafico
chart = Highchart()


def ndvi(in_nir_band, in_colour_band, in_rows, in_cols, in_geotransform, out_tiff, data_type=gdal.GDT_Float32):

    """
    Performs an NDVI calculation given two input bands, as well as other information that can be retrieved from the
    original image.
    @param in_nir_band A GDAL band object representing the near-infrared image data.
    @type in_nir_band GDALRasterBand
    @param in_colour_band A GDAL band object representing the colour image data.
    @type: in_colour_band GDALRasterBand
    @param in_rows The number of rows in both input bands.
    @type: in_rows int
    @param in_cols The number of columns in both input bands.
    @type: in_cols int
    @param in_geotransform The geographic transformation to be applied to the output image.
    @type in_geotransform Tuple (as returned by GetGeoTransform())
    @param out_tiff Path to the desired output .tif file.
    @type: out_tiff String (should end in ".tif")
    @param data_type Data type of output image.  Valid values are gdal.UInt16 and gdal.Float32.  Default is
                      gdal.Float32
    @type data_type GDALDataType
    @return None
    """



    #Leia as faixas de entrada como matrizes numpy.
    np_nir    = in_nir_band.ReadAsArray(0, 0, in_cols, in_rows)
    np_colour = in_colour_band.ReadAsArray(0, 0, in_cols, in_rows)

    # Converta os arrays np em ponto flutuante de 32 bits para garantir que a divisao ocorra corretamente.
    np_nir_as32    = np_nir.astype(np.float32)
    np_colour_as32 = np_colour.astype(np.float32)


    #Tratando divisao por zero
    np.seterr(divide='ignore', invalid='ignore')

    # Calculando a formula NDVI  = (nir + red) / ( nir + red)
    numerator   = subtract(np_nir_as32, np_colour_as32)
    denominator = add(np_nir_as32, np_colour_as32)
    result      = divide(numerator, denominator)

    # Remova todas as areas fora do limite
    result[result == -0] = -99

    #capturando valores minimo e maximo com numpy
    np.nanmin(result), np.nanmax(result)

    #classe que noramliza a escala de cores
    class MidpointNormalize(colors.Normalize):

        def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
            self.midpoint = midpoint
            colors.Normalize.__init__(self,vmin,vmax,clip)

        def __call__(self, value, clip=None):
            x, y = [self.vmin, self.midpoint, self.vmax],[0,0.5,1]
            return np.ma.masked_array(np.interp(value,x,y), np.isnan(value))

    # definindo valores minimo e maximo para construcao do grafico        
    min = -1#np.nanmin(result);
    max = 1#np.nanmax(result);
    mid = 0.1
    
    #printando valores
    #print('Minimo ',min);
    #print('Maximo ',max);


    #criando imagem .png, demonstrando grafico escala falsa cor 
    fig  = plt.figure(figsize=(20,10))
    ax   = fig.add_subplot(111) 
    cmap = plt.cm.RdYlGn
    cax  = ax.imshow(result,cmap=cmap, clim=(min,max), norm=MidpointNormalize(midpoint=mid,vmin=min,vmax=max))
    ax.axis('off'),
    ax.set_title('NDVI', fontsize=18,fontweight='bold')
    cbar = fig.colorbar(cax, orientation='horizontal', shrink=0.65)
    fig.savefig('ndvi-escala.png', dpi=200,bbox_inches='tight', pad_inches=0.7)
    plt.show()

    #criando imagem com o histograma
    fig2 = plt.figure(figsize=(10,10))
    ax   = fig2.add_subplot(111)

    plt.title("Histograma NDVI", fontsize=18,fontweight='bold')
    plt.xlabel("Valores NDVI", fontsize=14)
    plt.ylabel("# pixels", fontsize=12)
    x = result[~np.isnan(result)]
    numBins = 20
    count   = len(x)
    lista   = [];
    i       = 0    
    while(i <= count):
        
        lista.append(x[i])
        i  = i + 1000

    ax.hist(lista,numBins,color='#43A047',alpha=0.8)

    fig2.savefig('ndvi-histograma.png', dpi=200,bbox_inches='tight',pad_inches=0.7)
    plt.show()

    #chart.add_data_set(lista,series_type='pie', name='NDVI Series')
    #chart.set_options('title',{'text':'NDVI'})
    #chart.save_file('grafico');


    #Inicializando o driver geotiff.
    geotiff = GetDriverByName('GTiff')

    # If the desired output is an int16, map the domain [-1,1] to [0,255], create an int16 geotiff with one band and
    # write the contents of the int16 NDVI calculation to it.  Otherwise, create a float32 geotiff with one band and
    # write the contents of the float32 NDVI calculation to it.
    if data_type == gdal.GDT_UInt16:
        ndvi_int8 = multiply((result + 1), (2**7 - 1))
        output = geotiff.Create(out_tiff, in_cols, in_rows, 1, gdal.GDT_Byte)
        output_band = output.GetRasterBand(1)
        output_band.SetNoDataValue(-99)
        output_band.WriteArray(ndvi_int8)
    elif data_type == gdal.GDT_Float32:
        output = geotiff.Create(out_tiff, in_cols, in_rows, 1, gdal.GDT_Float32)
        output_band = output.GetRasterBand(1)
        output_band.SetNoDataValue(-99)
        output_band.WriteArray(result)
    else:
        raise ValueError('Tipo de dados de saida invalidos. Os tipos validos sao gdal.UInt16 ou gdal.Float32.')

    # Set the geographic transformation as the input.
    output.SetGeoTransform(in_geotransform)

    return None


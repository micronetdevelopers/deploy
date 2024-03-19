from django.db import models

class MarsMainTableData(models.Model):
    DATACODE = models.CharField(max_length=10,unique=True)
    DATANAME = models.CharField(max_length=100)
    COMP_NA = models.CharField(max_length=50)
    SATT_NA = models.CharField(max_length=50)
    CL_REF = models.CharField(max_length=50)
    CL_ORDNA =	models.CharField(max_length=50)
    CL_PROJNA =	models.CharField(max_length=100)
    CL_PURPOSE = models.CharField(max_length=100)
    CL_ADDRESS1	= models.CharField(max_length=150)
    CL_ADDRESS2	= models.CharField(max_length=150)
    SEN_NAME =	models.CharField(max_length=20)
    IMG_DATYPE = models.CharField(max_length=30)
    IMG_DAPROC = models.CharField(max_length=20)
    IMG_DATE =	models.CharField(max_length=10)
    IMG_DT_RNG = models.CharField(max_length=21)
    DLOCA_CY =	models.CharField(max_length=100)
    DLOCA_ST =	models.CharField(max_length=100)
    DLOCA_DT =	models.CharField(max_length=100)
    DLOCA_LOCA = models.CharField(max_length=100)
    DAREA =	models.FloatField()
    DSIZE = models.CharField(max_length=10)
    DQLNAME = models.CharField(max_length=100)
    DFORMAT = models.CharField(max_length=20)
    DCLOUD = models.FloatField()
    DSNOW = models.FloatField() 	
    D_AQ_BITS =	models.IntegerField()
    D_PR_BITS =	models.IntegerField()
    DPRJ_TABLE = models.CharField(max_length=20)
    DPRJ_NAME =	models.CharField(max_length=6)
    D_NROWS =	models.IntegerField()	
    D_NCOLS =	models.IntegerField()
    D_NBANDS =	models.IntegerField()	
    D_NTILES =	models.IntegerField()	
    D_TYPE =	models.CharField(max_length=20)
    D_NBITS =	models.IntegerField()	
    D_SIGN =	models.CharField(max_length=10)
    D_IN_ANGL =	models.FloatField()
    D_GSD_AXT =	models.FloatField()
    D_GSD_ALT =	models.FloatField()
    D_PIXELX =	models.FloatField()
    D_PIXELY =	models.FloatField()
    AL_DA_PATH = models.CharField(max_length=150)
    AL_SH_PATH = models.CharField(max_length=150)
    AL_QL_PATH = models.CharField(max_length=150)
    XML_FILE =	models.CharField(max_length=100)

    def __str__(self):
        return self.DATACODE  
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['DATACODE'], name='unique_datacode')
        ]

class MarsBandInformation(models.Model):
    DATACODE = models.ForeignKey(MarsMainTableData, to_field='DATACODE', on_delete=models.CASCADE, related_name='marsbandinformation')
    BAND_NAME = models.CharField(max_length=30)
    BAND_S_SPEC = models.FloatField()
    BAND_E_SPEC = models.FloatField()

    def __str__(self):
        return f"{self.DATACODE.DATACODE} - {self.BAND_NAME}"

class MarsBoundsCoordinates(models.Model):
    DATACODE = models.ForeignKey(MarsMainTableData, to_field='DATACODE', on_delete=models.CASCADE, related_name='marsboundscoordinates')
    COOD_NO = models.IntegerField()
    COOD_XX = models.FloatField()
    COOD_YY = models.FloatField()

    def __str__(self):
        return f"{self.DATACODE.DATACODE} - {self.COOD_NO}"



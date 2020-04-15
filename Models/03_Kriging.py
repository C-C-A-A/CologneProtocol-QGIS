# Import modules
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterExpression
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterDestination
import processing
# for Function look_for_precalculated_values()
from qgis.core import QgsProject


class _kriging(QgsProcessingAlgorithm):

    # Initalize input parameters
    def initAlgorithm(self, config=None):
        # Call function to look for precalculated values in layer "Bounding Geometry"
        self.look_for_precalculated_values()
        
        self.addParameter(QgsProcessingParameterVectorLayer('sites', 'LEC', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('hubdistlecradii', 'HubDist_LEC_Radii', type=QgsProcessingParameterField.Numeric, parentLayerParameterName='sites', allowMultiple=False, defaultValue='HubDist'))
        self.addParameter(QgsProcessingParameterNumber('gridcellsize', 'Grid_Cellsize', type=QgsProcessingParameterNumber.Integer, defaultValue=1000))
        self.addParameter(QgsProcessingParameterExpression('formel', 'Formel', parentLayerParameterName='', defaultValue=self.formula_default))
        self.addParameter(QgsProcessingParameterNumber('lagdist', 'LagDist', type=QgsProcessingParameterNumber.Double, defaultValue=self.lag_dist_default))
        self.addParameter(QgsProcessingParameterBoolean('BlockKriging', 'Block_Kriging', defaultValue=True))
        self.addParameter(QgsProcessingParameterNumber('blocksize', 'Block_Size', type=QgsProcessingParameterNumber.Integer, defaultValue=100))
        self.addParameter(QgsProcessingParameterNumber('maxsearchdist', 'Max_Search_Dist', type=QgsProcessingParameterNumber.Integer, defaultValue=self.max_search_dist_default))
        self.addParameter(QgsProcessingParameterNumber('numberofptsmin', 'Number_of_Pts_Min', type=QgsProcessingParameterNumber.Integer, defaultValue=3))
        self.addParameter(QgsProcessingParameterNumber('numberofptsmax', 'Number_of_Pts_Max', type=QgsProcessingParameterNumber.Integer, defaultValue=10))
        self.addParameter(QgsProcessingParameterRasterDestination('Kriging_raster', 'Kriging_Raster', createByDefault=True, defaultValue="Kriging.sdat"))
        self.addParameter(QgsProcessingParameterRasterDestination('Quality_measure', 'Quality_Measure', optional=True, createByDefault=False, defaultValue="Variance.sdat"))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Step 7: Ordinary kriging
        alg_params = {
            'BLOCK': parameters['BlockKriging'],
            'DBLOCK': parameters['blocksize'],
            'FIELD': parameters['hubdistlecradii'],
            'LOG': False,
            'POINTS': parameters['sites'],
            'SEARCH_DIRECTION': 0,
            'SEARCH_POINTS_ALL': 0,
            'SEARCH_POINTS_MAX': parameters['numberofptsmax'],
            'SEARCH_POINTS_MIN': parameters['numberofptsmin'],
            'SEARCH_RADIUS': parameters['maxsearchdist'],
            'SEARCH_RANGE': 0,
            'TARGET_USER_FITS': 0,
            'TARGET_USER_SIZE': parameters['gridcellsize'],
            'TARGET_USER_XMIN TARGET_USER_XMAX TARGET_USER_YMIN TARGET_USER_YMAX': None,
            'TQUALITY': 1,
            'VAR_MAXDIST': parameters['maxsearchdist'],
            'VAR_MODEL': parameters['formel'],
            'VAR_NCLASSES': parameters['lagdist'],
            'VAR_NSKIP': 1,
            'PREDICTION': parameters['Kriging_raster'],
            'VARIANCE': parameters['Quality_measure']
        }
        outputs['OrdinaryKriging'] = processing.run('saga:ordinarykriging', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Kriging_raster'] = outputs['OrdinaryKriging']['PREDICTION']
        results['Quality_measure'] = outputs['OrdinaryKriging']['VARIANCE']
        return results

    def name(self):
        return '03_Kriging'

    def displayName(self):
        return '03_Kriging'

    def group(self):
        return 'Cologne-Protocol'

    def groupId(self):
        return 'Cologne-Protocol'

    def createInstance(self):
        return _kriging()

    def look_for_precalculated_values(self):
        try:
            layer = QgsProject.instance().mapLayersByName("Bounding Geometry")[0]
            self.max_search_dist_default = round(layer.getFeature(0).attributes()[3],2)
            self.lag_dist_default = round(layer.getFeature(0).attributes()[4],2)
        except:
            self.max_search_dist_default = ""
            self.lag_dist_default = ""
        try:
            layer = QgsProject.instance().mapLayersByName("Variogram Results")[0]
            self.formula_default = layer.getFeature(1).attributes()[6]
        except:
            self.formula_default = ""

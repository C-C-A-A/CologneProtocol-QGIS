from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterVectorDestination
import processing


class _postprocessing(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('krigingraster', 'Kriging_Raster', defaultValue="Kriging_Raster"))
        self.addParameter(QgsProcessingParameterVectorLayer('sites', 'sites', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('contourmin', 'Contour_Min', type=QgsProcessingParameterNumber.Integer, defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber('contourmax', 'Contour_Max', type=QgsProcessingParameterNumber.Integer, defaultValue=25000))
        self.addParameter(QgsProcessingParameterNumber('contourequidist', 'Contour_Equidist', type=QgsProcessingParameterNumber.Integer, defaultValue=500))
        self.addParameter(QgsProcessingParameterVectorDestination('Contour_line', 'Contour_Line', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorDestination('Contour_poly_area_n', 'Contour_Poly_area_n', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Contour lines
        alg_params = {
            'GRID': parameters['krigingraster'],
            'VERTEX': 1,
            'ZMAX': parameters['contourmax'],
            'ZMIN': parameters['contourmin'],
            'ZSTEP': parameters['contourequidist'],
            'CONTOUR': parameters['Contour_line']
        }
        outputs['ContourLines'] = processing.run('saga:contourlines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Contour_line'] = outputs['ContourLines']['CONTOUR']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Add row number
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'ID_MODEL',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 1,
            'FORMULA': '@row_number',
            'INPUT': parameters['sites'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddRowNumber'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Convert lines to polygons
        alg_params = {
            'LINES': outputs['ContourLines']['CONTOUR'],
            'POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvertLinesToPolygons'] = processing.run('saga:convertlinestopolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Polygon dissolve (by attribute)
        alg_params = {
            'BND_KEEP': True,
            'FIELD_1': 'Z',
            'FIELD_2': None,
            'FIELD_3': None,
            'POLYGONS': outputs['ConvertLinesToPolygons']['POLYGONS'],
            'DISSOLVED': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonDissolveByAttribute'] = processing.run('saga:polygondissolvebyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Polygon properties
        alg_params = {
            'BAREA         ': True,
            'BLENGTH       ': False,
            'BPARTS        ': True,
            'BPOINTS       ': False,
            'POLYGONS': outputs['PolygonDissolveByAttribute']['DISSOLVED'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonProperties'] = processing.run('saga:polygonproperties', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Point statistics for polygons
        alg_params = {
            'AVG             ': False,
            'DEV             ': False,
            'FIELDS': 'ID_MODEL',
            'FIELD_NAME': 3,
            'MAX             ': False,
            'MIN             ': False,
            'NUM             ': True,
            'POINTS': outputs['AddRowNumber']['OUTPUT'],
            'POLYGONS': outputs['PolygonProperties']['OUTPUT'],
            'SUM             ': False,
            'VAR             ': False,
            'STATISTICS': parameters['Contour_poly_area_n']
        }
        outputs['PointStatisticsForPolygons'] = processing.run('saga:pointstatisticsforpolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Contour_poly_area_n'] = outputs['PointStatisticsForPolygons']['STATISTICS']
        return results

    def name(self):
        return '04_Post-Processing'

    def displayName(self):
        return '04_Post-Processing'

    def group(self):
        return 'Cologne-Protocol'

    def groupId(self):
        return 'Cologne-Protocol'

    def createInstance(self):
        return _postprocessing()

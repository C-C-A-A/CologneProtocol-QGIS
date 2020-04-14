# Import Models
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFileDestination
from qgis.core import QgsProcessingParameterFeatureSink
import processing

# Initalize Input Parameters
class _preprocessing(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('sites', 'Sites', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFileDestination('Lec_statistics', 'LEC_Statistics', optional=True, fileFilter='HTML files (*.html)', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('BoundingGeometry', 'Bounding Geometry', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Lec', 'LEC', type=QgsProcessing.TypeVectorPoint, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Vertices_cleaned', 'Vertices_cleaned', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Sites_cleaned', 'Sites_cleaned', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Voronoi', 'Voronoi', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(13, model_feedback)
        results = {}
        outputs = {}

        # Step 1: Delete duplicate sites
        alg_params = {
            'INPUT': parameters['sites'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteDuplicateSites'] = processing.run('qgis:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Step 2: Creating Voronoi polygons
        alg_params = {
            'BUFFER': 0,
            'INPUT': outputs['DeleteDuplicateSites']['OUTPUT'],
            'OUTPUT': parameters['Voronoi']
        }
        outputs['VoronoiPolygons'] = processing.run('qgis:voronoipolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Voronoi'] = outputs['VoronoiPolygons']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Add row_number (ID)
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Vertices_ID',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 1,
            'FORMULA': ' @row_number ',
            'INPUT': outputs['DeleteDuplicateSites']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': parameters['Sites_cleaned']
        }
        outputs['AddSites_cleanId'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Sites_cleaned'] = outputs['AddSites_cleanId']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extract layer extent (Bounding Box)
        alg_params = {
            'INPUT': outputs['VoronoiPolygons']['OUTPUT'],
            'ROUND_TO': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractLayerExtent'] = processing.run('qgis:polygonfromlayerextent', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Step 3: Extraction of vertices
        alg_params = {
            'INPUT': outputs['VoronoiPolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractVertices'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Step 4: Aggregation of vertices
        alg_params = {
            'INPUT': outputs['ExtractVertices']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteDuplicateGeometries'] = processing.run('qgis:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Step 5a: Calculate Statistics - Bounding Box Diagonal
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Diagonal',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '(sqrt(\"WIDTH\"^2+\"HEIGHT\"^2))',
            'INPUT': outputs['ExtractLayerExtent']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Add rownumber (ID) to Vertices_Cleaned
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Vertices_ID',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 1,
            'FORMULA': '@row_number',
            'INPUT': outputs['DeleteDuplicateGeometries']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': parameters['Vertices_cleaned']
        }
        outputs['AddVerticesId'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Vertices_cleaned'] = outputs['AddVerticesId']['OUTPUT']

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # # Step 5a: Calculate Statistics - MaxSearchDist
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'MaxSearchDist',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '(sqrt(\"WIDTH\"^2+\"HEIGHT\"^2))/2',
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator2'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

       # Step 5a: Calculate Statistics - Lag Distance
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'LagDist',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '(sqrt(\"WIDTH\"^2+\"HEIGHT\"^2))/250',
            'INPUT': outputs['FieldCalculator2']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator3'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Step 5: Defining the radius of the „Largest Empty Circle“
        alg_params = {
            'FIELD': 'Vertices_ID',
            'HUBS': outputs['AddSites_cleanId']['OUTPUT'],
            'INPUT': outputs['AddVerticesId']['OUTPUT'],
            'UNIT': 0,
            'OUTPUT': parameters['Lec']
        }
        outputs['DistanceToNearestHubPoints'] = processing.run('qgis:distancetonearesthubpoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Lec'] = outputs['DistanceToNearestHubPoints']['OUTPUT']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Drop field(s) from BoundingGeometry
        alg_params = {
            'COLUMN': ['MINX','MINY','MAXX','MAXY','CNTX','CNTY','AREA','PERIM'],
            'INPUT': outputs['FieldCalculator3']['OUTPUT'],
            'OUTPUT': parameters['BoundingGeometry']
        }
        outputs['DropFields'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['BoundingGeometry'] = outputs['DropFields']['OUTPUT']

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Step 5: Calculate Basic Statistics for HubDist (LEC-Radii)
        alg_params = {
            'FIELD_NAME': 'HubDist',
            'INPUT_LAYER': outputs['DistanceToNearestHubPoints']['OUTPUT'],
            'OUTPUT_HTML_FILE': parameters['Lec_statistics']
        }
        outputs['BasicStatisticsForFields'] = processing.run('qgis:basicstatisticsforfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Lec_statistics'] = outputs['BasicStatisticsForFields']['OUTPUT_HTML_FILE']
        return results

    def name(self):
        return '01_Pre-Processing'

    def displayName(self):
        return '01_Pre-Processing'

    def group(self):
        return 'Cologne-Protocol'

    def groupId(self):
        return 'Cologne-Protocol'

    def createInstance(self):
        return _preprocessing()

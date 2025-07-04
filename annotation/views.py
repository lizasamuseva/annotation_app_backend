import logging
import os

from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from annotation.helpers.annotation_manager import AnnotationManager
from annotation.helpers.utils.constants.supported_requests_types import \
    RequestContentType
from annotation.helpers.utils.constants.constants import CACHE_KEY_PARSED_RML, \
    CACHE_KEY_ALL_POSSIBLE_FILTERS, CACHE_KEY_REQUIRED_FILTERS, KEY_IN_REQUEST_REQUIRED_FILTERS, CACHE_KEY_EPPG_PATH
from annotation.helpers.utils.custom_exceptions import MissingRMLKeyError, InvalidRMLStructure, \
    EPPGFileInvalid, SessionExpired
from annotation.helpers.utils.file_manager import FileManager
from annotation.helpers.utils.filters import Filters
from annotation.helpers.utils.parser_rml import ParserRML
from annotation.helpers.utils.validation.file_validation.eppg_validation import EPPGValidation
from annotation.helpers.utils.validation.file_validation.rml_validation import RMLValidation
from annotation.helpers.utils.validation.filter_validation import FilterValidation
from annotation.helpers.utils.validation.request_validation import RequestValidation
from annotation.serializers import FiltersResponseSerializer

logger = logging.getLogger(__name__)


class HelloWorldView(APIView):
    """
    Responds with "Hello world!"

    Responses:
        - 200 OK:
            Response successful
    """

    parser_class = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="""
    Respond with "Hello world!"
    """,
        responses={
            200: "Hello world!"
        }
    )
    def get(self, request):
        return Response("Hello world!")


class GetFiltersView(APIView):
    """
    Processes an uploaded RML file to extract all available filters.
    Saves the dictionary version of the RML.

    Steps:
        - Validates the RML (PSG) file.
        - Parses it into a dictionary.
        - Extracts all available filters.
        - Caches the parsed data and filters.

    Responses:
        - 200 OK:
            The file was successfully parsed and filters returned in JSON format.
        - 400 BAD_REQUEST:
            The uploaded file or request did not pass validation.
        - 422 UNPROCESSABLE_ENTITY:
            The RML file is malformed or missing required XML nodes.
        - 500 INTERNAL_SERVER_ERROR:
            An unexpected server error occurred.
    """

    parser_classes = [MultiPartParser]

    # localhost: https://localhost:8000/static/sample.rml
    @swagger_auto_schema(
        operation_description="""
        Upload an RML (PSG) file using the form key `RML_src`.

        📎 [Click here to download a sample RML file](https://psg.e4.iomt.sk/annotate-eppg/static/sample.rml)

        The API parses the file and returns available filters in JSON format.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="RML_src",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="RML (PSG) file to upload"
            )
        ],
        responses={
            200: openapi.Response(
                description="Returns extracted filters",
                schema=FiltersResponseSerializer()
            ),
            400: "Bad Request - validation error",
            422: "Unprocessable Entity - Invalid RML structure",
            500: "Internal Server Error",
        }
    )
    def post(self, request):
        path_to_rml = None
        # This will ensure a session is created
        request.session.modified = True
        try:
            # Step 1: validation
            uploaded_file = RMLValidation(request).validate()

            # Step 2: Save the file temporarily in memory for use during the current request
            path_to_rml = FileManager.within(uploaded_file)

            # Step 3: Parse file into dict form and save dict in cache
            parsed_rml = ParserRML.parse_rml_to_dict(path_to_rml)
            FileManager.save_cache(request, CACHE_KEY_PARSED_RML, parsed_rml)

            # Step 4: Extract the filters and save in cache
            all_possible_filters = Filters(parsed_rml)
            FileManager.save_cache(request, CACHE_KEY_ALL_POSSIBLE_FILTERS,
                                   all_possible_filters.get_filters())

            return Response({"result": {"filters": all_possible_filters.get_filters()}}, status=status.HTTP_200_OK)

        # Catch any validation error
        except ValidationError as ve:
            return Response({"error": str(ve.detail[0]) if isinstance(ve.detail, list) else str(ve.detail)},
                            status=status.HTTP_400_BAD_REQUEST)

        # Catch the Error, if the RML doesn't contain the keys in dictionary, which are required for further processing
        # Or whether the structure of the rml doesn't correspond to XML
        except (MissingRMLKeyError, InvalidRMLStructure) as invalidError:
            return Response({"error": str(invalidError)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception as e:
            logger.error(f"Unexpected error in GetFiltersView.", exc_info=True)
            return Response({
                "error": "An unexpected error occurred. Please contact support."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if path_to_rml:
                FileManager.cleanup_file(path_to_rml)


class ProcessUserFiltersView(APIView):
    """
    Validates and stores the user-selected filters.

    Steps:
        - Validates the JSON structure and filter content.
        - Saves validated filters to the cache.

    Responses:
        - 204 NO_CONTENT:
            Filters were successfully validated and stored.
        - 400 BAD_REQUEST:
            The filters or request body are invalid.
        - 500 INTERNAL_SERVER_ERROR:
            An unexpected server error occurred.
    """

    @staticmethod
    def validate_request_filters(request):
        """
        Validates the filter format and checks if all filters are allowed.
        """

        RequestValidation.content_type(request, RequestContentType.JSON)
        required_filters = FilterValidation.has_correct_format(request.data, KEY_IN_REQUEST_REQUIRED_FILTERS)
        FilterValidation.are_filters_allowed(request, required_filters)
        return required_filters

    @swagger_auto_schema(
        operation_description="Validates and stores user-selected filters. The input JSON should contain the filters under the `filters` key.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'filters': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'Neuro': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            example=["Arousal"]
                        ),
                        'SpO2': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            example=["RelativeDesaturation"]
                        ),
                        'Nasal': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            example=["Snore"]
                        ),
                        'Cardiac': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            example=["Tachycardia"]
                        ),
                        'SleepStages': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            example=["Wake", "NonREM2", "NonREM1"]
                        ),
                        'BodyPositions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            example=["Supine"]
                        ),
                    },
                    example={
                        "Neuro": ["Arousal"],
                        "SpO2": ["RelativeDesaturation"],
                        "Nasal": ["Snore"],
                        "Cardiac": ["Tachycardia"],
                        "SleepStages": ["Wake", "NonREM2", "NonREM1"],
                        "BodyPositions": ["Supine"]
                    }
                )
            }
        ),
        responses={
            204: 'Filters validated and stored successfully',
            400: 'Bad Request - validation error',
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        try:
            # Step 1: Validate the request json and get the filters required by client
            required_filters = self.validate_request_filters(request)

            # Step 2: Save required filters to the cache
            FileManager.save_cache(request, CACHE_KEY_REQUIRED_FILTERS, required_filters)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValidationError as ve:
            logger.error(f"Unexpected error in ProcessUserFiltersView.", exc_info=True)
            return Response({
                'error': str(ve.detail[0]) if isinstance(ve.detail, list) else str(ve.detail)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error in ProcessUserFiltersView.", exc_info=True)
            return Response({
                'error': 'An unexpected error occurred. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadEPPGFileView(APIView):
    """
    Validates and uploads the ePPG file.

    Steps:
        - Validates the file format and headers.
        - Saves the file to the MEDIA directory.
        - Stores the file path in cache.

    Responses:
        - 204 NO_CONTENT:
            File uploaded and cached successfully.
        - 400 BAD_REQUEST:
            File or request validation failed.
        - 422 UNPROCESSABLE_ENTITY:
            File has an invalid or missing header.
        - 500 INTERNAL_SERVER_ERROR:
            An unexpected server error occurred.
    """

    parser_classes = [MultiPartParser]

    # localhost: http://localhost:8000/static/sample_eppg.txt
    @swagger_auto_schema(
        operation_description="""
        Upload an ePPG file under the form key `EPPG_src`. 
        📎 [Click here to download a sample ePPG sample file](https://psg.e4.iomt.sk/annotate-eppg/static/sample_eppg.txt)
        API validates and caches the file.""",
        manual_parameters=[
            openapi.Parameter(
                name='EPPG_src',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='The ePPG file to upload'
            )
        ],
        responses={
            204: 'File uploaded and cached successfully',
            400: 'Bad Request - validation error',
            422: 'Unprocessable Entity - Invalid or missing header',
            500: 'Internal Server Error',
        }
    )
    def post(self, request):
        try:
            # Step 1: validation
            uploaded_file = EPPGValidation(request).validate()

            # Step 2: Persist the file across requests
            eppg_path = FileManager.across(uploaded_file)

            # Step 3: Save the path into the cache
            FileManager.save_cache(request, CACHE_KEY_EPPG_PATH, eppg_path)

            return Response(status=status.HTTP_204_NO_CONTENT)

        # Catch any validation error
        except ValidationError as ve:
            return Response({'error': str(ve.detail[0]) if isinstance(ve.detail, list) else str(ve.detail)},
                            status=status.HTTP_400_BAD_REQUEST)

        # Catch Error if the EPPG file doesn't contain appropriate header/previous request is expired
        except (EPPGFileInvalid, SessionExpired) as ee:
            return Response({'error': str(ee)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception:
            logger.error(f"Unexpected error in ProcessUserFiltersView.", exc_info=True)
            return Response({
                'error': 'An unexpected error occurred. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnnotateView(APIView):
    """
    Performs annotation on the uploaded ePPG file using the parsed PSG data and selected filters.

    Inputs:
        - RML_dict: Dictionary parsed from the RML (PSG) file.
        - EPPG_path: Path to the uploaded ePPG file.
        - filters: User-selected filters.

    Responses:
        - 200 OK:
            Returns the annotated ePPG file for download.
        - 409 CONFLICT:
            ePPG file not found (e.g., expired cache).
        - 422 UNPROCESSABLE_ENTITY:
            Time mismatch between PSG and ePPG files exceeds allowed range (8 hours).
        - 500 INTERNAL_SERVER_ERROR:
            Output file was not generated or an unexpected error occurred.
    """

    @swagger_auto_schema(
        operation_description="Annotates the uploaded ePPG file with PSG data and selected filters, then returns the annotated file for download.",
        responses={
            200: openapi.Response(
                description="Returns the annotated ePPG file for download.",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='binary',
                    description='Annotated ePPG file'
                )
            ),
            409: openapi.Response(
                description="The ePPG file was not found (possibly expired cache)."
            ),
            422: openapi.Response(
                description="Time mismatch between PSG and ePPG files exceeds allowed range (8 hours)."
            ),
            500: openapi.Response(
                description="An unexpected server error occurred or output file was not generated."
            ),
        }
    )
    def get(self, request):
        eppg_path = None
        output_file_path = None
        try:
            # Get user oriented information
            rml_dict = FileManager.get_cache(request, CACHE_KEY_PARSED_RML)

            eppg_path = FileManager.get_cache(request, CACHE_KEY_EPPG_PATH)
            filters = FileManager.get_cache(request, CACHE_KEY_REQUIRED_FILTERS)

            # Annotate the file
            annotation_manager = AnnotationManager(rml_dict, eppg_path, filters)
            output_file_path = annotation_manager.add_annotations()

            # Respond with the annotated output file
            if os.path.exists(output_file_path):
                file = open(output_file_path, 'rb')
                filename = os.path.basename(eppg_path)
                response = FileResponse(file, content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="{filename.split(".")[0]}_Annotated.txt"'
                return response
            else:
                return Response({
                    'error': 'Something went wrong. Please, try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except SessionExpired:
            return Response({
                'error': SessionExpired
            }, status=status.HTTP_409_CONFLICT)

        except EPPGFileInvalid as error:
            return Response({
                'error': str(error)
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception:
            logger.error(f"Unexpected error in AnnotateView.", exc_info=True)
            return Response({
                'error': 'An unexpected error occurred. Please contact support.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if eppg_path:
                FileManager.cleanup_file(eppg_path)
            if output_file_path:
                FileManager.cleanup_file(output_file_path)

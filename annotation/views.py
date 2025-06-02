import logging
import os
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from django.core.cache import cache
from annotation.customFunctions.AnnotationManager import AnnotationManager
from annotation.customFunctions.Utilities.Constants.SupportedRequestsTypes import \
    RequestContentType
from annotation.customFunctions.Utilities.Constants.constants import CACHE_KEY_PARSED_RML, \
    CACHE_KEY_ALL_POSSIBLE_FILTERS, CACHE_KEY_REQUIRED_FILTERS, KEY_IN_REQUEST_REQUIRED_FILTERS, CACHE_KEY_EPPG_PATH
from annotation.customFunctions.Utilities.FileManager import FileManager
from annotation.customFunctions.Utilities.Filters import Filters
from annotation.customFunctions.Utilities.ParserRML import ParserRML
from annotation.customFunctions.Utilities.Validation.FileValidation.EPPGValidation import EPPGValidation
from annotation.customFunctions.Utilities.Validation.FileValidation.RMLValidation import RMLValidation
from annotation.customFunctions.Utilities.Validation.FilterValidation import FilterValidation
from annotation.customFunctions.Utilities.Validation.RequestValidation import RequestValidation
from annotation.customFunctions.Utilities.CustomExceptions import MissingRMLKeyError, InvalidRMLStructure, EppgFileInvalid

logger = logging.getLogger(__name__)

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

    def post(self, request):
        path_to_RML = None
        # This will ensure a session is created
        request.session.modified = True
        try:
            # Step 1: Validation
            uploaded_file = RMLValidation(request).validate()

            # Step 2: Save the file temporarily in memory for use during the current request
            path_to_RML = FileManager.process_temporally_file_saving_WITHIN_REQUEST(uploaded_file)

            # Step 3: Parse file into dict form and save dict in cache
            parsed_rml = ParserRML.parse_RML_to_Dict(path_to_RML)
            FileManager.save_entity_to_the_cache(request, CACHE_KEY_PARSED_RML, parsed_rml)

            # Step 4: Extract the filters and save in cache
            all_possible_filters = Filters(parsed_rml)
            FileManager.save_entity_to_the_cache(request, CACHE_KEY_ALL_POSSIBLE_FILTERS, all_possible_filters.get_filters())

            return Response({'result': {"filters" : all_possible_filters.get_filters()}}, status=status.HTTP_200_OK)
        # Catch any validation error
        except ValidationError as ve:
            return Response({'error': str(ve.detail[0]) if isinstance(ve.detail, list) else str(ve.detail)}, status=status.HTTP_400_BAD_REQUEST)
        # Catch the Error, if the RML doesn't contain the keys in dictionary, which are required for further processing
        # Or whether the structure of the rml doesn't correspond to XML
        except (MissingRMLKeyError, InvalidRMLStructure) as invalidError:
            return Response({'error': str(invalidError)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            logger.error(f"Unexpected error in GetFiltersView.")
            return Response({
                'error': 'An unexpected error occurred. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if path_to_RML:
                FileManager.cleanup_file(path_to_RML)


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
    def validate_request_filters(self, request):
        """
        Validates the filter format and checks if all filters are allowed.
        """
        RequestValidation.content_type(request, RequestContentType.JSON)
        required_filters = FilterValidation.has_correct_format(request.data, KEY_IN_REQUEST_REQUIRED_FILTERS)
        FilterValidation.are_filters_allowed(request, required_filters)
        return required_filters

    def post(self, request):
        try:
            # Step 1: Validate the request json and get the filters required by client
            required_filters = self.validate_request_filters(request)

            # Step 2: Save required filters to the cache
            FileManager.save_entity_to_the_cache(request, CACHE_KEY_REQUIRED_FILTERS , required_filters)
            logger.error(required_filters)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as ve:
            return Response({
                'error': str(ve.detail[0]) if isinstance(ve.detail, list) else str(ve.detail)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in ProcessUserFiltersView.")
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
    def post(self, request):
        try:
            # Step 1: Validation
            uploaded_file = EPPGValidation(request).validate()

            # Step 2: Persist the file across requests
            EPPG_path = FileManager.process_persistent_file_saving_ACROSS_REQUESTS(uploaded_file)

            # Step 3: Save the path into the cache
            FileManager.save_entity_to_the_cache(request, CACHE_KEY_EPPG_PATH, EPPG_path)

            return Response(status=status.HTTP_204_NO_CONTENT)
        # Catch any validation error
        except ValidationError as ve:
            return Response({'error': str(ve.detail[0]) if isinstance(ve.detail, list) else str(ve.detail)}, status=status.HTTP_400_BAD_REQUEST)
        # Catch Error if the EPPG file doesn't contain appropriate header
        except EppgFileInvalid as ee:
            return Response({'error': str(ee)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            logger.error(f"Unexpected error in ProcessUserFiltersView.")
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
    def get(self, request):
        EPPG_path = None
        output_file_path = None
        try:
            # Get user oriented information
            RML_dict = cache.get(request.session[CACHE_KEY_PARSED_RML])
            EPPG_path = cache.get(request.session[CACHE_KEY_EPPG_PATH])
            filters = cache.get(request.session[CACHE_KEY_REQUIRED_FILTERS])

            # Annotate the file
            annotation_manager = AnnotationManager(RML_dict, EPPG_path, filters)
            output_file_path = annotation_manager.add_annotations()

            # Respond with the annotated output file
            if os.path.exists(output_file_path):
                file = open(output_file_path, 'rb')
                filename = os.path.basename(EPPG_path)
                response = FileResponse(file, content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="{filename.split(".")[0]}_Annotated.txt"'
                return response
            else:
                return Response({
                    'error': 'Something went wrong. Please, try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except FileNotFoundError:
            return Response({
                'error': "The ePPG file wasn't found. Please, load it again."
            }, status=status.HTTP_409_CONFLICT)
        except EppgFileInvalid as error:
            return Response({
                'error': error
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            logger.error(f"Unexpected error in AnnotateView.")
            return Response({
                'error': 'An unexpected error occurred. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if EPPG_path:
                FileManager.cleanup_file(EPPG_path)
            if output_file_path:
                FileManager.cleanup_file(output_file_path)
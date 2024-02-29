12344444from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from Sebi_Api.settings import BASE_DIR2
from .models import *
from datetime import datetime
from django.http import Http404
from rest_framework import status
import zipfile
from io import BytesIO
from django.shortcuts import render, HttpResponse
import json
from django.http import JsonResponse,request

from django.http import HttpResponse
import json
import zipfile
from io import BytesIO
from django.urls import reverse
from django.views import View
import io
import csv

from django.http import HttpResponse
import zipfile
from io import BytesIO
from django.views import View
from .models import sebi_orders, mca_orders
from django.core.serializers.json import DjangoJSONEncoder


from rest_framework import renderers
from django.core.exceptions import ValidationError
# from django.core.validators import validate_date
from django.db.models import Q

import os
from django.conf import settings

import datetime   

from pathlib import Path   
import tempfile
import calendar    

        
import os
import zipfile
from django.http import HttpResponse
from django.views import View
from rest_framework import status
from .models import sebi_orders        
from datetime import datetime


# Define the custom HTML renderer
class HTMLRenderer(renderers.BaseRenderer):
    media_type = 'text/html'
    format = 'html'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        html_content = '<html><body>'
        for entry in data['result']:
            html_content += f'<p>Date: {entry["date_of_order"]}</p>'
            html_content += f'<p>Title: {entry["title_of_order"]}</p>'
            html_content += f'<p>Type Of Order: {entry["type_of_order"]}</p>'
            html_content += f'<p>Link to Order: {entry["link_to_order"]}</p>'
            html_content += f'<p>PDF File Path: {entry["pdf_file_path"]}</p>'
            html_content += f'<p>PDF File Name: {entry["pdf_file_name"]}</p>'
            html_content += f'<p>Date Scraped: {entry["date_scraped"]}</p>'
            html_content += '<hr />'
            
         # Add the total PDF download link to the HTML content
        html_content += f'<p>Total Count: {data["total_count"]}</p>' 
        html_content += f'<p>{data["total_pdf_download_link"]}</p>'    
        html_content += '</body></html>'
        return html_content.encode(self.charset)





def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except:
       return False

class Custom404View(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"result": "Resource not found", 'status': status.HTTP_404_NOT_FOUND})




# # Define your API view
class GetOrderDateView(APIView):
    # renderer_classes = [HTMLRenderer]  # Set the custom renderer
    # renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer]

    def get(self, request, *args, **kwargs):
        try:
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
        except ValueError:
            return Response({"result": "Invalid limit or offset value, must be an integer"}, status = status.HTTP_422_UNPROCESSABLE_ENTITY)

        date = str(request.GET.get('date', None))
        type_of_order = kwargs.get('type_of_order')  # Extract 'type_of_order' parameter from URL

        if date:
            if len(date) != 10 or not validate_date(date):
                return Response({"result": "Incorrect date format, should be YYYY-MM-DD"}, status =  status.HTTP_422_UNPROCESSABLE_ENTITY)



            valid_parameters = {'limit', 'offset', 'date'}
            provided_parameters = set(request.GET.keys())

            if not valid_parameters.issuperset(provided_parameters):
                return Response({"result": "Invalid query parameters, check spelling for given parameters"}, status = status.HTTP_400_BAD_REQUEST)
            
            try:
                # Filter queryset based on 'type_of_order' parameter
                if type_of_order == 'ed_cgm':
                    order_details = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order='ed_cgm').values('date_of_order',  'title_of_order', 'type_of_order', 'link_to_order',  'pdf_file_path', 'pdf_file_name', 'updated_date',  'date_scraped')[offset:limit]
                    total_count = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order='ed_cgm').count()
                elif type_of_order == 'ao_cgm':
                    order_details = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order='ao_cgm').values('date_of_order',  'title_of_order', 'type_of_order', 'link_to_order',  'pdf_file_path', 'pdf_file_name', 'updated_date',  'date_scraped')[offset:limit]
                    total_count = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order='ao_cgm').count()
                elif type_of_order == 'settlementorder':
                    order_details = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order='settlementorder').values('date_of_order',  'title_of_order', 'type_of_order', 'link_to_order',  'pdf_file_path', 'pdf_file_name', 'updated_date',  'date_scraped')[offset:limit]
                    total_count = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order='settlementorder').count()
                else:
                    return Response({"result": "Invalid 'type_of_order' parameter"}, status = status.HTTP_400_BAD_REQUEST)

                
                
                print("order_details :", order_details)
                if len(order_details) > 0:
                    # Modify 'pdf_file_name' field to include a hyperlink for downloading the PDF file
                    # for entry in order_details:
                        # Construct the URL to the Download PDF view with the PDF filename as a parameter
                        # download_pdf_url = reverse('download_pdf', kwargs={'filename': entry['pdf_file_name']})
                        # entry['pdf_file_name'] = f'<a href="{download_pdf_url}">Download PDF</a>'
                    
                    
                    #Create a total download link for all PDFs displayed
                
                    # total_pdf_download_url = reverse('download_all_pdfs', kwargs={'date': date, 'whether': whether}) + f'?limit={limit}&offset={offset}'

                    # total_pdf_download_link = f'{total_pdf_download_url}'
                    
                    # Create download link for the zip file
                    total_pdf_download_link = request.build_absolute_uri('/api/v1/{}/download_pdfs/?date={}'.format(type_of_order, date))+ f'&limit={limit}&offset={offset}' 

                    
                    # Return JSON response with results including the total PDF download link
                    return Response({"result": order_details, 'total_count': total_count, 'total_pdf_download_link': total_pdf_download_link}, status=status.HTTP_200_OK)
                else:
                    return Response({"result": "No Data Provided in your specific date!!!."}, status = status.HTTP_401_UNAUTHORIZED)
            except TimeoutError:
                return Response({"result": "timeout error"}, status = status.HTTP_502_BAD_GATEWAY)
            except Exception as err:
                return Response({"result": f"An internal server error occurred: {err}"}, status =  status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
           raise Http404("Page not found")





class DownloadPDFsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            
            # Check if the limit is above 500 and raise an exception if so
            if limit > 500:
                return Response({"result": "Limit should not exceed 500"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as ve:
            return Response({"result": str(ve)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        date = request.GET.get('date')
        type_of_order = kwargs.get('type_of_order')  # Extract 'type_of_order ' parameter from URL
        
        BASE_DIR2 = 'C:\\Users\\Premkumar.8265\\Desktop\\'  # Update with your base directory
        print("BASE_DIR2: ", BASE_DIR2)
        
        try:
            if date:
                try:
                    validate_date(date)
                except ValidationError:
                    return Response({"result": "Incorrect date format, should be YYYY-MM-DD"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                valid_parameters = {'limit', 'offset', 'date'}
                provided_parameters = set(request.GET.keys())

                if not valid_parameters.issuperset(provided_parameters):
                    return Response({"result": "Invalid query parameters, check spelling for given parameters"}, status=status.HTTP_400_BAD_REQUEST)

                root_directory = os.path.join(settings.MEDIA_ROOT, type_of_order)
                print("Root directory:", root_directory)  # Check the root directory

                year, month, day = date.split('-')
                month_names = {
                    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                }
                month_name = month_names[int(month)]
                print("Year:", year)  # Check the year
                print("Month:", month_name)  # Check the month name
                
                # Retrieve all orders for the specified date
                order_details = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order=type_of_order)[offset:limit]

                print("order_details:", order_details)  
                
                pdf_paths = [os.path.join(BASE_DIR2, order.pdf_file_path.lstrip('/')) for order in order_details]

                print("PDF paths:", pdf_paths)  # Check the PDF paths
                
                if pdf_paths:
                    temp_file = tempfile.NamedTemporaryFile(delete=False)
                    with zipfile.ZipFile(temp_file, 'w') as zip_file:
                        for pdf_path in pdf_paths:
                            if os.path.exists(pdf_path):
                                zip_file.write(pdf_path, os.path.relpath(pdf_path, BASE_DIR2))
                            else:
                                # If the PDF file is missing, log an error or return a message
                                print("Error: The file does not exist:", pdf_path)
                                return Response({"result": f"PDF file {pdf_path} is missing"}, status=status.HTTP_404_NOT_FOUND)

                    temp_file.close()
                    temp_file = open(temp_file.name, 'rb')
                    data = temp_file.read()
                    temp_file.close()
                    os.unlink(temp_file.name)
                    
                    response = HttpResponse(data, content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename="Sebi_pdf_files.zip"'
                    
                    return response
                else:
                    return HttpResponse("No PDF files found for the specified date.", status=status.HTTP_404_NOT_FOUND)
            else:
                return HttpResponse("Date parameter is required.", status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return HttpResponse("Invalid limit or offset value, must be an integer", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except ValidationError:
            return HttpResponse("Incorrect date format, should be YYYY-MM-DD", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            print("Error:", e)  # Debugging statement
            return HttpResponse("An error occurred.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# class DownloadPDFsView(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             limit = int(request.GET.get('limit', 50))
#             offset = int(request.GET.get('offset', 0))
            
#             # Check if the limit is above 500 and raise an exception if so
#             if limit > 500:
#                 raise ValueError("Limit should not exceed 500")
#         except ValueError as ve:
#             return Response({"result": str(ve)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

#         date = str(request.GET.get('date', None))
#         type_of_order = kwargs.get('type_of_order')  # Extract 'type_of_order ' parameter from URL
        
        
#         # Build paths inside the project like this: BASE_DIR2 / 'subdir'.
#         BASE_DIR2 = 'C:\\Users\\Premkumar.8265\\Desktop\\'
#         print("BASE_DIR2: ", BASE_DIR2)
        
#         try:
#             if date:
#                 try:
#                     validate_date(date)
#                 except ValidationError:
#                     return Response({"result": "Incorrect date format, should be YYYY-MM-DD"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

#                 valid_parameters = {'limit', 'offset', 'date'}
#                 provided_parameters = set(request.GET.keys())

#                 if not valid_parameters.issuperset(provided_parameters):
#                     return Response({"result": "Invalid query parameters, check spelling for given parameters"}, status=status.HTTP_400_BAD_REQUEST)

#                 # Define the root directory based on type_of_order
#                 root_directory = os.path.join(settings.MEDIA_ROOT, type_of_order)
#                 print("root_directory : ", root_directory)
                 
#                # Extract year and month from the date
#                 year, month, _ = date.split('-')
#                 month_names = {
#                     1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
#                     7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
#                 }
#                 # Get the month name from the month number
#                 month_name = month_names[int(month)]

#                 # Construct the directory path based on date
#                 directory_path = os.path.join(root_directory, year, month_name)
#                 print("directory_path : ", directory_path)
                
#                 # Check if the directory exists
#                 if not os.path.exists(directory_path):
#                     return Response("Directory not found.", status=404)

#                 # Query the necessary number of PDFs based on both limit and offset parameters
#                 order_details = sebi_orders.objects.filter(date_scraped__startswith=date, type_of_order=type_of_order).values('pdf_file_name')[offset:limit]
#                 print("order_details : ", order_details)

#                 # Filter the PDFs based on sr_no values
#                 pdf_paths = [os.path.join(directory_path, entry['pdf_file_name']) for entry in order_details if entry['pdf_file_name']]
#                 print("pdf_paths : ", pdf_paths)
                
#                 if pdf_paths:
#                     # Create an HttpResponse object with content type as zip
#                     response = HttpResponse(content_type='application/zip')

#                     # Set the zip file name
#                     response['Content-Disposition'] = 'attachment; filename="Sebi_pdf_files.zip"'
                    
                    
#                     # Create a zip file
#                     with zipfile.ZipFile(response, 'w') as zip_file:
#                         # Add each PDF file to the zip
#                         for pdf_path in pdf_paths:
#                             pdf_file = os.path.join(settings.MEDIA_ROOT, pdf_path)  # Append .pdf if not already present
#                             print("pdf_file: ",  pdf_file)
#                             if os.path.exists(pdf_file):
#                                 zip_file.write(pdf_file, arcname=os.path.basename(pdf_file))
                    
#                                 print("zip_file : ", zip_file)
#                             else:
#                                 # If the PDF file is missing, log an error or return a message
#                                 print(f"PDF file {pdf_file} is missing from the pdfdownload folder")                                     # You can log this error or return a response indicating the missing file # For example, you can 
#                                 return Response({"result": f"PDF file {pdf_file} is missing"}, status=status.HTTP_404_NOT_FOUND)
#                     return response
#                 else:
#                     # If no PDF files were found, return an empty response
#                     return HttpResponse("No PDF files found.", status=404)
#             else:
#                 return HttpResponse("Date parameter is required.", status=status.HTTP_400_BAD_REQUEST)
#         except ValueError:
#             return HttpResponse("Invalid limit or offset value, must be an integer", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
#         except ValidationError:
#             return HttpResponse("Incorrect date format, should be YYYY-MM-DD", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
#         except Exception as e:
#             print("Error:", e)  # Debugging statement
#             return HttpResponse("An error occurred.", status=500)






  


  
  
  
        
 
def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

class Custom404View(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"result": "Resource not found", 'status': status.HTTP_404_NOT_FOUND})


#function for querying the endpoint using year and month and date on which pdfs are updated in websites, here month and date are optioanl.


class GetOrderYearView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            limit = int(request.GET.get('limit', 1))
            offset = int(request.GET.get('offset', 0))
            year = request.GET.get('year')
            month = request.GET.get('month')
            date = request.GET.get('date')
            
            if date:
                print("Original date:", date)
                date = date.zfill(2)
                print("Formatted date:", date)
                
        except ValueError:
            return Response({"result": "Invalid limit or offset value, must be an integer", 'status':status.HTTP_422_UNPROCESSABLE_ENTITY})

        type_of_order = kwargs.get('type_of_order')

        valid_parameters = {'limit', 'offset', 'year', 'month', 'date'}
        provided_parameters = set(request.GET.keys())

        if not valid_parameters.issuperset(provided_parameters):
            return Response({"result": "Invalid query parameters, check spelling for given parameters", 'status': status.HTTP_400_BAD_REQUEST})

        try:
            queryset = sebi_orders.objects.filter(type_of_order=type_of_order)

            if year:
                queryset = queryset.filter(date_of_order__icontains=year)

            if month:
                # Convert the month name to its abbreviation
                queryset = queryset.filter(date_of_order__icontains=month)
                # month_abbr = datetime.strptime(month, '%m').strftime('%b')
                # queryset = queryset.filter(date_of_order__contains=f"{month_abbr}")

            if date:
                 # Ensure single-digit dates are formatted with a leading zero
                date = date.zfill(2)
                print("Filtering by date:", date)
                queryset = queryset.filter(
                    Q(date_of_order__contains=f" {date},") |  # Match for ' 02,'
                    Q(date_of_order__startswith=f"{date},") |  # Match for '02,'
                    Q(date_of_order__endswith=f", {date}") |  # Match for ', 02'
                    Q(date_of_order__exact=date)  # Match for '02' as a standalone date
                )
                print(queryset.query)
                print("queryset:", queryset)

            order_details = queryset.values('date_of_order', 'title_of_order', 'type_of_order', 'link_to_order', 'pdf_file_path', 'pdf_file_name', 'updated_date', 'date_scraped')[offset:limit]
            print("order_details:", order_details)
            total_count = queryset.count()

            if len(order_details) > 0:
                total_pdf_download_link = request.build_absolute_uri(f'/api/v1/{type_of_order}/download_all_pdfs/?year={year}&month={month}&date={date}&limit={limit}&offset={offset}') 
                
                return Response({"result": order_details, 'total_count': total_count, 'total_pdf_download_link': total_pdf_download_link}, status=status.HTTP_200_OK)
            else:
                return Response({"result": "No Data Provided in your specific date", 'status': status.HTTP_401_UNAUTHORIZED})
        except TimeoutError:
            return Response({"result": "timeout error", 'status': status.HTTP_502_BAD_GATEWAY})
        except Exception as err:
            return Response({"result": f"An internal server error occurred: {err}", 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
        
 

class DownloadAllPDFsView(View):
    def get(self, request, *args, **kwargs):
        try:
            limit = int(request.GET.get('limit', 1))
            offset = int(request.GET.get('offset', 0))
            year = request.GET.get('year')
            month = request.GET.get('month')
            date = request.GET.get('date')
            type_of_order = kwargs.get('type_of_order')
            
        except ValueError:
            return HttpResponse("Invalid limit or offset value, must be an integer", status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            queryset = sebi_orders.objects.filter(type_of_order=type_of_order)

            if year:
                queryset = queryset.filter(date_of_order__icontains=year)

            if month and date != 'None':
                month_abbr = datetime.strptime(month, '%m').strftime('%b')
                queryset = queryset.filter(date_of_order__contains=f"{month_abbr}")

                
            if date and date != 'None':  # Check if date is provided and not 'None'
                queryset = queryset.filter(date_of_order__contains=date)
                print("queryset :", queryset)

            pdf_paths = [entry.pdf_file_name for entry in queryset if entry.pdf_file_name]
            print("pdf_paths:", pdf_paths)
            
            if pdf_paths:
                response = HttpResponse(content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="Sebi_pdf_files.zip"'
                
                with zipfile.ZipFile(response, 'w') as zip_file:
                    for pdf_path in pdf_paths[offset:offset+limit]:
                        pdf_file = os.path.join(settings.MEDIA_ROOT, pdf_path)
                        if os.path.exists(pdf_file):
                            zip_file.write(pdf_file, arcname=os.path.basename(pdf_file))
                            print("Zip_file :", zip_file)

                return response
            else:
                return HttpResponse("No PDF files found.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Error:", e)
            return HttpResponse("An error occurred.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

 
 

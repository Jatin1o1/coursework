import os
import sys
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
from  Course_maker.course_maker import CourseGenerator
from test import generate_course


def home(request):
    return JsonResponse({'message': 'Hello from ai_endpoint!'})

@csrf_exempt
def generate_response(request):

    print("\n\n\t\t  got request ")
    brief = request.GET.get('query', '')
    target_audience = request.GET.get('target_audience', 'begginers')
    course_duration = request.GET.get('course_duration', '5 weeks')
    
    course_gen = CourseGenerator()
    response = course_gen.generate_course(brief, target_audience, course_duration)
    # response = generate_course(brief, target_audience, course_duration)
    return JsonResponse(response, safe=False)

    try:
        if isinstance(response, str):  # If response is a string, attempt to parse it
            response_json = json.loads(response)
        elif isinstance(response, dict):  # If response is already a dictionary, use it
            response_json = response
        else:
            return JsonResponse({"error": "Invalid response format from CourseGenerator"}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Failed to parse JSON from CourseGenerator"}, status=500)

    # ✅ Return properly formatted JSON with indentation
    return JsonResponse(response_json, json_dumps_params={"indent": 4}, safe=False)

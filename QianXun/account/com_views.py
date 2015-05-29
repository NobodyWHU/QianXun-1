from django.shortcuts import render_to_response

from utils.Decorator import token_required, post_required, exception_handled
from utils.Serializer import json_response_from_object, json_response
from utils.SendMsg import MobSMS
from conf.resp_code import *
from conf.default_value import ZONE
from forms import PaginationForm, VerifycodeValidationForm
from QianXun.account.db import window, verifycode
from QianXun.orders.db import promotion


def index(request):
    return render_to_response('test/testCommon.html')


@exception_handled
@token_required
@post_required
def common_window_display_bycanteen(request):
    pagination_form = PaginationForm(request.POST)
    if pagination_form.is_valid() and request.POST['canteen'] and request.POST['canteen'].isdigit():
        pagination_dict = pagination_form.cleaned_data
        canteen_id = request.POST['canteen']
        window_bean_list = window.get_window_bean_list_bycanteen(canteen_id, pagination_dict)
        return json_response_from_object(OK, window_bean_list, 'windowList')
    else:
        return json_response(PARAM_REQUIRED, CODE_MESSAGE.get(PARAM_REQUIRED))


@exception_handled
@token_required
@post_required
def common_window_display_byname(request):
    pagination_form = PaginationForm(request.POST)
    if pagination_form.is_valid() and request.POST['window_name'] and len(request.POST['window_name']) <= 64\
            and request.POST['school'] and request.POST['school'].isdigit():
        pagination_dict = pagination_form.cleaned_data
        window_name = request.POST['window_name']
        school_id = request.POST['school']
        window_bean_list = window.get_window_bean_list_byname(school_id, window_name, pagination_dict)
        return json_response_from_object(OK, window_bean_list, 'windowList')
    else:
        return json_response(PARAM_REQUIRED, CODE_MESSAGE.get(PARAM_REQUIRED))


@exception_handled
@token_required
@post_required
def common_window_display_byprotype(request):
    pagination_form = PaginationForm(request.POST)
    if pagination_form.is_valid() and request.POST['pro_type'] and request.POST['pro_type'].isdigit() \
            and request.POST['school'] and request.POST['school'].isdigit():
        pagination_dict = pagination_form.cleaned_data
        pro_type_id = request.POST['pro_type']
        school_id = request.POST['school']
        window_id_list = promotion.get_window_id_list_byprotype(school_id, pro_type_id, pagination_dict)
        window_bean_list = window.get_window_bean_list_byid(window_id_list)
        return json_response_from_object(OK, window_bean_list, 'windowList')
    else:
        return json_response(PARAM_REQUIRED, CODE_MESSAGE.get(PARAM_REQUIRED))


@exception_handled
@token_required
@post_required
def common_verifycode_validation(request):
    verifycode_validation_form = VerifycodeValidationForm(request.POST)
    if verifycode_validation_form.is_valid():
        sms = MobSMS()
        verifycode_validation_dict = verifycode_validation_form.cleaned_data
        zone = ZONE
        phone = verifycode_validation_dict['user_name']
        code = verifycode_validation_dict['verify_code']
        result = sms.verify_sms_code(zone, phone, code)
        if result.get('status', 500) == 200:
            verifycode.create(verifycode_validation_form)
            return json_response(OK, CODE_MESSAGE.get(OK))
        else:
            return json_response(CODE_INVALID, result)
    else:
        return json_response(PARAM_REQUIRED, CODE_MESSAGE.get(PARAM_REQUIRED))

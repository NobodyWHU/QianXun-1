from django.shortcuts import render_to_response

from utils.Decorator import customer_token_required, post_required, exception_handled
from utils.Serializer import json_response_from_object, json_response, json_back
from utils.MakeSerialNumber import get_serial_number
from utils.CostCalculator import get_vip_discount, get_promotions_discount, get_deliver_cost
from conf.resp_code import *
from conf.enum_value import ORDER_STATUS
from conf.default_value import ORDER_DISH_MAX, PROMOTION_MAX
from forms import OrderForm, OrderConfirmForm, OrderDetailDisplayForm, PaginationForm, CustomerOrderUpdateForm, CommentForm
from db import dish, promotion, order, orderdish
from QianXun.account.db import customer


def index(request):
    return render_to_response('test/testOrder.html')


@exception_handled
@customer_token_required
@post_required
def customer_order_create(request):
    order_form = OrderForm(request.POST)
    dish_list_str = request.POST.get("dish_list")
    if order_form.is_valid() and dish_list_str and dish_list_str.startswith("[{") and dish_list_str.endswith("}]"):
        order_dict = order_form.cleaned_data
        dish_list = json_back(dish_list_str)
        # calculate the food cost
        if len(dish_list) <= ORDER_DISH_MAX:
            cost = dish.get_dish_list_cost(dish_list)
            customer_model = request.user_meta['customer_model']
            window_id = order_dict['window'].id
            if customer.has_vip_balance(customer_model):    # customer is a valid VIP, and has VIP balance
                cost = get_vip_discount(cost)
            else:                                           # window has promotion_list
                promotion_list = promotion.get_promotion_list_bywindow(window_id, {'page': 1, 'count': PROMOTION_MAX})
                cost = get_promotions_discount(cost, promotion_list)

            # initial the order_dict
            order_dict.update({'customer': customer_model})
            order_dict.update({'order_id': get_serial_number(window_id)})
            order_dict.update({'food_cost': cost})
            order_dict.update({'deliver_cost': get_deliver_cost()})
            my_order_bean = order.create_bycus(order_dict)  # create a record in orders table,return a model with an id

            # add orders_dishes
            for my_dish in dish_list:
                my_order_dish_bean = orderdish.create(my_order_bean.id, my_dish)
                my_order_bean.dish_list.append(my_order_dish_bean)
            return json_response_from_object(OK, my_order_bean)
        else:
            return json_response(ORDER_DISH_REACH_MAX, CODE_MESSAGE.get(ORDER_DISH_REACH_MAX))
    else:
        return json_response(PARAM_REQUIRED, order_form.errors)


@exception_handled
@customer_token_required
@post_required
def customer_order_display(request):
    pagination_form = PaginationForm(request.POST)
    if pagination_form.is_valid():
        pagination_dict = pagination_form.cleaned_data
        customer_id = request.user_meta['customer_model'].id
        order_status = pagination_dict['order_status']
        order_bean_list = order.get_order_bean_list_bycus(customer_id, order_status, pagination_dict)
        return json_response_from_object(OK, order_bean_list, 'order_list')
    else:
        return json_response(PARAM_REQUIRED, pagination_form.errors)


@exception_handled
@customer_token_required
@post_required
def customer_order_display_detail(request):
    order_detail_display_form = OrderDetailDisplayForm(request.POST)
    if order_detail_display_form.is_valid():
        order_detail_display_dict = order_detail_display_form.cleaned_data
        customer_id = request.user_meta['customer_model'].id
        order_detail_bean = order.get_order_detail_byid_bycus(customer_id, order_detail_display_dict)
        return json_response_from_object(OK, order_detail_bean)
    else:
        return json_response(PARAM_REQUIRED, CODE_MESSAGE.get(PARAM_REQUIRED))


@exception_handled
@customer_token_required
@post_required
def customer_order_confirm(request):
    order_confirm_form = OrderConfirmForm(request.POST)
    if order_confirm_form.is_valid():
        order_confirm_dict = order_confirm_form.cleaned_data
        customer_id = request.user_meta['customer_model'].id
        impact = order.update_bycus(customer_id, order_confirm_dict)
        if impact == 1:
            return json_response(OK, CODE_MESSAGE.get(OK))
        else:
            return json_response(DB_ERROR, CODE_MESSAGE.get(DB_ERROR))
    else:
        return json_response(PARAM_REQUIRED, order_confirm_form.errors)


@exception_handled
@customer_token_required
@post_required
def customer_order_update(request):
    order_update_form = CustomerOrderUpdateForm(request.POST)
    if order_update_form.is_valid():
        order_update_dict = order_update_form.cleaned_data
        customer_id = request.user_meta['customer_model'].id
        impact = order.update_status_bycus(customer_id, order_update_dict)
        if impact == 1:
            return json_response(OK, CODE_MESSAGE.get(OK))
        else:
            return json_response(DB_ERROR, CODE_MESSAGE.get(DB_ERROR))
    else:
        return json_response(PARAM_REQUIRED, order_update_form.errors)


@exception_handled
@customer_token_required
@post_required
def customer_order_delete(request):
    if request.POST['data']:
        order_id_list_str = request.POST['data']  # not the serial number,but the id
        order_id_list = json_back(order_id_list_str)
        customer_id = request.user_meta['customer_model'].id
        order_id_list_fail_to_delete = order.delete_bycus(customer_id, order_id_list)
        return json_response_from_object(OK, order_id_list_fail_to_delete, 'order_id_list')
    else:
        return json_response(PARAM_REQUIRED, CODE_MESSAGE.get(PARAM_REQUIRED))


@exception_handled
@customer_token_required
@post_required
def customer_comment_create(request):
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment_dict = comment_form.cleaned_data
        customer_id = request.user_meta['customer_model'].id
        my_order = order.get_order_byid_bycus(customer_id, comment_dict)
        if my_order.order_status == ORDER_STATUS[6][0]:  # user can only make comment on order in complete status
            comment_bean = orderdish.update_comment(my_order, comment_dict)
            return json_response_from_object(OK, comment_bean)
        else:
            return json_response(ORDER_STATUS_ERROR, CODE_MESSAGE.get(ORDER_STATUS_ERROR))
    else:
        return json_response(PARAM_REQUIRED, CODE_MESSAGE.get(PARAM_REQUIRED))



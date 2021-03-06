__author__ = 'Hannah'

from QianXun.orders.models import OrdersDishes
from QianXun.orders.beans import OrderDishBean, CommentBean
from utils.Pagination import get_paginator
from datetime import datetime


def create(orders_id, dish_json):
    order_dish_model = OrdersDishes()
    order_dish_model.orders_id = orders_id
    order_dish_model.dish_id = dish_json['dish_id']
    order_dish_model.number = dish_json['number']
    order_dish_model.save()
    return order_dish_model


def get_order_dish_byid(order_model, orderdish_dict):
    order_dish_model = order_model.ordersdishes_set.get(id__exact=orderdish_dict['orders_dishes'])
    return order_dish_model


def get_dish_list_byorder(order_model):
    order_dish_list = order_model.ordersdishes_set.all()
    return order_dish_list


def get_dish_bean_list_byorder(order_model):
    order_dish_list = order_model.ordersdishes_set.all()
    order_dish_bean_list = []
    for order_dish in order_dish_list:
        order_dish_bean = OrderDishBean(order_dish)
        order_dish_bean_list.append(order_dish_bean)
    return order_dish_bean_list


# used when calculate grade
def get_comment_list_bydish(dish_model):
    calculate_time = dish_model.calculate_time
    order_dish_model_list = dish_model.ordersdishes_set.filter(comment_time__gte=calculate_time)
    return order_dish_model_list


def get_comment_bean_list_bydish(dish_id, pagination_dict):
    paginator = get_paginator(pagination_dict)
    comment_list = OrdersDishes.objects.filter(dish_id=dish_id, grade__isnull=False).order_by('-comment_time')[paginator[0]: paginator[1]]
    comment_bean_list = []
    for comment in comment_list:
        comment_bean = CommentBean(comment)
        comment_bean_list.append(comment_bean)
    return comment_bean_list


def update_comment(order_model, comment_json):
    comment_model = order_model.ordersdishes_set.get(id__exact=comment_json['orders_dishes'])
    comment_model.grade = comment_json['grade']
    comment_model.text = comment_json['text']
    comment_model.comment_time = datetime.now()
    comment_model.save()
    return comment_model


def update_reply(order_dish_model, reply_dict):
    order_dish_model.reply = reply_dict['reply']
    order_dish_model.reply_time = datetime.now()
    order_dish_model.save()
    return order_dish_model
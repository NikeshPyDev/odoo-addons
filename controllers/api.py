# -*- coding: utf-8 -*-
from functools import wraps
from odoo.http import Controller, Response, request, route


def has_valid_token(api_fun):

    @wraps(api_fun)
    def wrapper(api_req, *args, **kwargs):
        authorization_header = request.httprequest.headers.get('Authorization')
        auth_type, access_token = authorization_header.split(" ")
        uid = request.env['res.users'].sudo().search([('access_token', '=', access_token)])
        if uid:
            return api_fun(api_req, *args, **kwargs)
        else:
            return Response(response="Authentication failed!!", status=401)
    return wrapper


class RestApi(Controller):

    @route('/user/auth', type="json", auth='public', methods=["POST"], csrf=False)
    def authenticate_user(self):
        data = request.jsonrequest
        db = data.get("db")
        login = data.get("login")
        password = data.get("password")
        user_id =request.session.authenticate(db, login, password)
        res = {"msg": "Authentication failed"}
        if user_id:
            user = request.env['res.users'].browse(user_id)
            if user:
                access_token = user.sudo().generate_access_token()
                res =  request.env['ir.http'].session_info()
                res.update({"access_token": access_token})
        return res

    @route('/customer/update', type="json", auth='public', methods=["PUT"], csrf=False)
    @has_valid_token
    def update_customer(self):
        data = request.jsonrequest
        if data:
            customer_id =  data.get('customer_id')
            customer = request.env["res.partner"].browse(int(customer_id))
            contact_data_list = data.get('data')
            if customer:
                for cd in contact_data_list:
                    contact = {
                        "mobile": cd.get("mobile_no"),
                        "city": cd.get("city"),
                        "zip": cd.get("pin_code"),
                    }
                    state = request.env['res.country.state'].sudo().search([('name', '=', cd.get('state'))])
                    if state:
                        contact.update({"state_id": state.id})
                    if cd.get("address") == "Address1 - Billing":
                        contact.update({"type": "invoice"})
                    if cd.get("address") == "Address2 - Shipping":
                        contact.update({"type": "delivery"})
                    customer.sudo().write({'child_ids': [(0, 0, contact)]})

                return {"session_valid":True,
                        "response_code":200,
                        "status":"success",
                        "message_code":"CONTACTS_SAVED",
                        "message":"Contact information updated successfully.",
                        "payload":[]}
        return {"message": "Customer not found"}



# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

no_cache = 1
import frappe
from webshop.webshop.shopping_cart.cart import get_cart_quotation


def get_context(context):
	context.body_class = "product-page"
	if frappe.form_dict:
		quot_name = frappe.form_dict.quot_name
		context.update(get_cart_quotation(quot_name))
	else:	
		context.update(get_cart_quotation())

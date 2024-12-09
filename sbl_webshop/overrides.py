import frappe
from frappe import _, throw
from frappe.website.utils import is_signup_disabled
from frappe.utils import cint, escape_html, random_string,cstr
import requests
from webshop.webshop.utils.product import get_web_item_qty_in_stock
from frappe.model.workflow import set_workflow_state_on_action,apply_workflow
from erpnext.selling.doctype.quotation.quotation import _make_sales_order
from webshop.webshop.shopping_cart.cart import _get_cart_quotation
from frappe.contacts.doctype.contact.contact import get_contact_name
from frappe.core.doctype.user.user import create_contact
from erpnext.portal.utils import create_party_contact
from frappe.utils import get_url,getdate
from erpnext.accounts.doctype.payment_request.payment_request import (
	PaymentRequest as OriginalPaymentRequest,
)
from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
from erpnext import get_default_company


@frappe.whitelist(allow_guest=True)
def user_sign_up(email: str, full_name: str, mobile_no:str,redirect_to: str) -> tuple[int, str]:
	print('--'*10)
	print(email, full_name, mobile_no,redirect_to)
	if is_signup_disabled():
		frappe.throw(_("Sign Up is disabled"), _("Not Allowed"))

	user = frappe.db.get("User", {"email": email})
	if user:
		if user.enabled:
			return 0, _("Already Registered")
		else:
			return 0, _("Registered but disabled")
	else:
		if frappe.db.get_creation_count("User", 60) > 300:
			frappe.respond_as_web_page(
				_("Temporarily Disabled"),
				_(
					"Too many customers signed up recently, so the registration is disabled. Please try back in an hour"
				),
				http_status_code=429,
			)

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": escape_html(full_name),
			"mobile_no": '+966'+mobile_no,
			"enabled": 1,
			"new_password": random_string(10),
			"user_type": "Website User",
		}
	)
	user.flags.ignore_permissions = True
	user.flags.ignore_password_policy = True
	user.insert()

	# set default signup role as per Portal Settings
	default_role = frappe.db.get_value("Portal Settings", None, "default_role")
	if default_role:
		user.add_roles(default_role)

	user.add_roles("Customer")
	# set_country_from_ip(None, user.name)
	if redirect_to:
		frappe.cache.hset("redirect_after_login", user.name, redirect_to)

	#  create customer and contact
	party_type="Customer"
	party = frappe.new_doc(party_type)
	fullname = frappe.utils.get_fullname(user)
	party.update(
			{
				"customer_name": fullname,
				"customer_type": "Individual",
			}
		)		
	party.flags.ignore_mandatory = True
	party.insert(ignore_permissions=True)	
	contact = frappe.new_doc("Contact")
	contact.update({"first_name": fullname, "email_id": user})
	contact.append("links", dict(link_doctype=party_type, link_name=party.name))
	contact.append("email_ids", dict(email_id=cstr(email), is_primary=True))
	contact.flags.ignore_mandatory = True
	contact.insert(ignore_permissions=True)	

	if user.flags.email_sent:
		return 1, _("Please check your email for verification")
	else:
		return 2, _("Please ask your administrator to verify your sign-up")
	
# def set_country_from_ip(login_manager=None, user=None):
# 	if not user and login_manager:
# 		user = login_manager.user
# 	user_country = frappe.db.get_value("User", user, "country")
# 	# if user_country:
# 	#    return
# 	frappe.db.set_value("User", user, "country", get_country_code())
# 	return

# def get_country_code():
# 	ip = frappe.local.request_ip
# 	res = requests.get(f"http://ip-api.com/json/{ip}")

# 	try:
# 		data = res.json()
# 		if data.get("status") != "fail":
# 			return frappe.db.get_value("Country", {"code": data.get("countryCode")}, "name")
# 	except Exception:
# 		pass
# 	return    

def update_website_context(context):
	default_lead_time_for_in_stock_items = frappe.db.get_value("Sbl Settings", None, "default_lead_time_for_in_stock_items")
	default_lead_time_for_out_of_stock_items = frappe.db.get_value("Sbl Settings", None, "default_lead_time_for_out_of_stock_items")
	if default_lead_time_for_in_stock_items:
		context["default_lead_time_for_in_stock_items"] = default_lead_time_for_in_stock_items
	if default_lead_time_for_out_of_stock_items:
		context["default_lead_time_for_out_of_stock_items"] = default_lead_time_for_out_of_stock_items

def get_out_of_stock_item_lead_time(item_code):
	item_level_lead_time_for_out_of_stock_item = frappe.db.get_value("Item", item_code, "custom_lead_time_for_out_of_stock_item")
	default_lead_time_for_out_of_stock_items = frappe.db.get_value("Sbl Settings", None, "default_lead_time_for_out_of_stock_items")	
	if item_level_lead_time_for_out_of_stock_item:
		return item_level_lead_time_for_out_of_stock_item
	else:
		return default_lead_time_for_out_of_stock_items

def get_in_stock_item_lead_time(item_code):
	item_level_lead_time_for_in_stock_item = frappe.db.get_value("Item", item_code, "custom_lead_time_for_in_stock_item")
	default_lead_time_for_in_stock_items = frappe.db.get_value("Sbl Settings", None, "default_lead_time_for_in_stock_items")
	if item_level_lead_time_for_in_stock_item:
		return item_level_lead_time_for_in_stock_item
	else:
		return default_lead_time_for_in_stock_items

def set_quotation_taxes_and_charges(self,method)	:
	if self.order_type == "Shopping Cart":
		taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=self.company)
		if taxes.get("taxes"):
			self.update(taxes)	


def set_lead_time_in_quotation(self,method)	:
	quotation_level_maximum_lead_time=0
	for item in self.items:
		# website_warehouse = frappe.db.get_value("Website Item", {"item_code": item.item_code}, "website_warehouse")
		is_stock_item = frappe.db.get_value("Item", item.item_code, "is_stock_item")
		if is_stock_item==1:
			item_stock = get_web_item_qty_in_stock(item.item_code,"website_warehouse")
			if not cint(item_stock.in_stock):
				item.custom_lead_time=get_out_of_stock_item_lead_time(item.item_code)
			if item.qty > item_stock.stock_qty:
				item.custom_lead_time=get_out_of_stock_item_lead_time(item.item_code)
			else:
				item.custom_lead_time=get_in_stock_item_lead_time(item.item_code)
			if cint(item.custom_lead_time)>quotation_level_maximum_lead_time:
				quotation_level_maximum_lead_time=item.custom_lead_time
	self.custom_maximum_lead_time=quotation_level_maximum_lead_time


@frappe.whitelist()		
def update_web_customer_remark(doc_name,web_customer_remark,counter=0):
	quot=frappe.get_doc('Quotation', doc_name)
	if counter==1:
		web_customer_remark=web_customer_remark+"\n"+quot.custom_web_customer_remark
	quot.custom_web_customer_remark=web_customer_remark
	quot.save(ignore_permissions=True)
	return True

@frappe.whitelist()	
def update_web_customer_preferred_delivery_date(doc_name,web_customer_preferred_delivery_date):
	quot=frappe.get_doc('Quotation', doc_name)
	quot.custom_customers_preferred_delivery_date=getdate(web_customer_preferred_delivery_date)
	quot.save(ignore_permissions=True)
	return True

@frappe.whitelist()
def place_quotation_for_review(doc_name,workflow_action):
	
	next_workflow_state= workflow_action
	quot=frappe.get_doc('Quotation', doc_name)
	workflow_name= quot.meta.get_workflow()
	print('next_workflow_state',next_workflow_state)
	if ((quot.status == "Draft" and quot.workflow_state != next_workflow_state)):
		apply_workflow(quot,next_workflow_state)
		if next_workflow_state!='Accept':
			msg=_("Quotation {0} is placed for {1}. We shall email you with next update. Thanks".format(doc_name,next_workflow_state))
			# response["_server_messages"] =
			return msg
		else:

			quotation = quot
			cart_settings = frappe.get_cached_doc("Webshop Settings")
			quotation.company = cart_settings.company

			quotation.flags.ignore_permissions = True
			print(quotation.docstatus)
			# quotation.submit()

			if quotation.quotation_to == "Lead" and quotation.party_name:
				# company used to create customer accounts
				frappe.defaults.set_user_default("company", quotation.company)

			if not (quotation.shipping_address_name or quotation.customer_address):
				frappe.throw(_("Set Shipping Address or Billing Address"))

			sales_order = frappe.get_doc(
				_make_sales_order(
					quotation.name, ignore_permissions=True
				)
			)
			sales_order.payment_schedule = []

			if not cint(cart_settings.allow_items_not_in_stock):
				for item in sales_order.get("items"):
					item.warehouse = frappe.db.get_value(
						"Website Item", {"item_code": item.item_code}, "website_warehouse"
					)
					is_stock_item = frappe.db.get_value("Item", item.item_code, "is_stock_item")

					if is_stock_item:
						item_stock = get_web_item_qty_in_stock(
							item.item_code, "website_warehouse"
						)
						if not cint(item_stock.in_stock):
							throw(_("{0} Not in Stock").format(item.item_code))
						if item.qty > item_stock.stock_qty:
							throw(
								_("Only {0} in Stock for item {1}").format(
									item_stock.stock_qty, item.item_code
								)
							)

			sales_order.flags.ignore_permissions = True
			sales_order.insert()
			sales_order.submit()

			if hasattr(frappe.local, "cookie_manager"):
				frappe.local.cookie_manager.delete_cookie("cart_count")

			return sales_order.name
		

class PaymentRequest(OriginalPaymentRequest):
	def make_invoice(self):
		print('make_invoicemake_invoice set_as_paidset_as_paid as sbl')
		# frappe.throw('it is sbl')
		ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)
		if hasattr(ref_doc, "order_type") and ref_doc.order_type == "Shopping Cart":
			from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

			si = make_sales_invoice(self.reference_name, ignore_permissions=True)
			si.allocate_advances_automatically = True
			taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=self.company)
			si.taxes_and_charges=taxes.get("taxes_and_charges")
			si.run_method("set_missing_values")
			si.run_method("set_advances")
			si.run_method("calculate_taxes_and_totals")
			# si.flags.ignore_validate = True
			si = si.insert(ignore_permissions=True)
			si.submit()

	def set_as_paid(self):
		print('set_as_paidset_as_paid as sbl')
		if self.payment_channel == "Phone":
			self.db_set({"status": "Paid", "outstanding_amount": 0})

		else:
			payment_entry = self.create_payment_entry()
			self.make_invoice()

			return payment_entry
			
	def on_payment_authorized(self, status=None):
		print('on_payment_authorizedon_payment_authorized  set_as_paidset_as_paid as sbl')
		if not status:
			return

		if status not in ("Authorized", "Completed"):
			return

		if not hasattr(frappe.local, "session"):
			return

		if frappe.local.session.user == "Guest":
			return

		if self.payment_channel == "Phone":
			return

		cart_settings = frappe.get_doc("Webshop Settings")

		if not cart_settings.enabled:
			return

		success_url = cart_settings.payment_success_url
		redirect_to = get_url("/orders/{0}".format(self.reference_name))

		if success_url:
			redirect_to = (
				{
					"Orders": "/orders",
					"Invoices": "/invoices",
					"My Account": "/me",
				}
			).get(success_url, "/me")

		self.set_as_paid()
		msg=_("Your payment to us is successful. Thanks")
		frappe.msgprint(msg,alert=True, indicator="green")
		return redirect_to

	@staticmethod
	def get_gateway_details(args):
		print('get_gateway_details  get_gateway_details set_as_paidset_as_paid as sbl')
		if args.order_type != "Shopping Cart":
			return super().get_gateway_details(args)

		cart_settings = frappe.get_doc("Webshop Settings")
		gateway_account = cart_settings.payment_gateway_account
		return super().get_payment_gateway_account(gateway_account)		
	
	
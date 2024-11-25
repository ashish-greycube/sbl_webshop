import frappe

def show_custom_signup():
	settings = frappe.get_single("Sbl Settings")
	if settings.sign_up_with_mobile and settings.sign_up_with_mobile==1:
		return "sbl_webshop/templates/signup-form.html"
	return "frappe/templates/signup.html"
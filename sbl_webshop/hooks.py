app_name = "sbl_webshop"
app_title = "Sbl Webshop"
app_publisher = "GreyCube Technologies"
app_description = "customization for sbl ecomm"
app_email = "admin@greycube.in"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "sbl_webshop",
# 		"logo": "/assets/sbl_webshop/logo.png",
# 		"title": "Sbl Webshop",
# 		"route": "/sbl_webshop",
# 		"has_permission": "sbl_webshop.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sbl_webshop/css/sbl_webshop.css"
# app_include_js = "/assets/sbl_webshop/js/sbl_webshop.js"

# include js, css files in header of web template
# web_include_css = "/assets/sbl_webshop/css/sbl_webshop.css"
# web_include_js = "/assets/sbl_webshop/js/sbl_webshop.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sbl_webshop/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "sbl_webshop/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sbl_webshop.utils.jinja_methods",
# 	"filters": "sbl_webshop.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sbl_webshop.install.before_install"
# after_install = "sbl_webshop.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sbl_webshop.uninstall.before_uninstall"
# after_uninstall = "sbl_webshop.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sbl_webshop.utils.before_app_install"
# after_app_install = "sbl_webshop.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sbl_webshop.utils.before_app_uninstall"
# after_app_uninstall = "sbl_webshop.utils.after_app_uninstall"
update_website_context = [
    "sbl_webshop.overrides.update_website_context",
]

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sbl_webshop.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Quotation": {
        "validate": [
            "sbl_webshop.overrides.set_lead_time_in_quotation",
        ],
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sbl_webshop.tasks.all"
# 	],
# 	"daily": [
# 		"sbl_webshop.tasks.daily"
# 	],
# 	"hourly": [
# 		"sbl_webshop.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sbl_webshop.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sbl_webshop.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sbl_webshop.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sbl_webshop.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sbl_webshop.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sbl_webshop.utils.before_request"]
# after_request = ["sbl_webshop.utils.after_request"]

# Job Events
# ----------
# before_job = ["sbl_webshop.utils.before_job"]
# after_job = ["sbl_webshop.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sbl_webshop.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


signup_form_template = "sbl_webshop.login.show_custom_signup"

jinja = {
    "methods": [
        "sbl_webshop.overrides.get_out_of_stock_item_lead_time",
        "sbl_webshop.overrides.get_in_stock_item_lead_time"
        ]
}
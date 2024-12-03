frappe.ui.form.on("Webshop Settings", {
	onload: function(frm) {
		frm.set_query('payment_gateway_account', function() {
			return { 'filters':
                 'payment_channel' ["in", ["Phone","Email"]],
                };
		});
	}
})
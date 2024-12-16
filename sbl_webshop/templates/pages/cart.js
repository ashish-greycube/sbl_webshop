// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// JS exclusive to /cart page
frappe.provide("webshop.webshop.shopping_cart");
var shopping_cart = webshop.webshop.shopping_cart;

$.extend(shopping_cart, {
	show_error: function(title, text) {
		$("#cart-container").html('<div class="msg-box"><h4>' +
			title + '</h4><p class="text-muted">' + text + '</p></div>');
	},

	bind_events: function() {
		shopping_cart.bind_place_order();
		shopping_cart.bind_place_quotation_for_review();
		shopping_cart.bind_request_quotation();
		shopping_cart.bind_counter_offer_dialog();
		shopping_cart.bind_change_qty();
		shopping_cart.bind_remove_cart_item();
		shopping_cart.bind_change_notes();
		shopping_cart.bind_coupon_code();
		shopping_cart.bind_web_customer_remark();
		shopping_cart.bind_web_customer_preferred_delivery_date();
	},
	bind_web_customer_preferred_delivery_date: function(){
		$('.web_customer_preferred_delivery_date').on('input', function() {
			const $input = $(this);
			const web_customer_preferred_delivery_date = $input.val();
			const doc_name = $input.attr('data-doc-name');
			console.log('web_customer_preferred_delivery_date',web_customer_preferred_delivery_date)
			return frappe.call({
				type: "POST",
				method: "sbl_webshop.overrides.update_web_customer_preferred_delivery_date",
				args : {
					doc_name : doc_name,
					web_customer_preferred_delivery_date: web_customer_preferred_delivery_date
				},
				callback: function(r) {
					console.log(r,'r')
					
					if (r && r.message){
						location.reload();
						console.log(r,'r')
					}
				}
			});			
		});		
	},
	bind_web_customer_remark: function(){
		console.log(2332222);
		$('.web_customer_remark').on('change','textarea', function() {
			const $textarea = $(this);
			const web_customer_remark = $textarea.val();
			const doc_name = $textarea.attr('data-doc-name');
			return frappe.call({
				type: "POST",
				method: "sbl_webshop.overrides.update_web_customer_remark",
				args : {
					doc_name : doc_name,
					web_customer_remark: web_customer_remark,
					counter: "0"
				},
				callback: function(r) {
					console.log(r,'r')
					
					if (r && r.message){
						location.reload();
						console.log(r,'r')
					}
				}
			});			
		});
	},
	bind_counter_offer_dialog: function() {
		$(".btn-counter-offer-dialog").on("click", function() {
			d=frappe.prompt([
				{
					label: 'Your input',
					fieldname: 'counter_offer_remark',
					fieldtype: 'Small Text',
					reqd: 1,
				}
			], (values) => {
				console.log(values.counter_offer_remark);
				frappe.run_serially([
					() => {
						return frappe.call({
							type: "POST",
							method: "sbl_webshop.overrides.update_web_customer_remark",
							args : {
								doc_name : $('.quotation-name').text(),
								web_customer_remark: values.counter_offer_remark,
								counter : "1"
							},
							callback: function(r) {
								console.log(r,'r')
								
								if (r && r.message){
									// location.reload();
									console.log(r,'1r')
								}
							}
						});
					},
					()=>{
						$('button[data-workflow-action="Counter Offer"]').trigger("click");
					}
				]);				
			}, 'Counter Offer Remark', 'Submit')
			d.get_close_btn().hide();
		});		
	},
	bind_place_quotation_for_review: function() {
		$(".btn-place-quotation-for-review").on("click", function() {
			let billing_adress_count=$('div[data-address-type="billing"]').length
			let shipping_address_count=$('div[data-address-type="shipping"]').length
			if (billing_adress_count==1 || shipping_address_count==1) {
				shopping_cart.place_quotation_for_review(this);
			}else{
				frappe.msgprint({title: __('Missing Address'),	indicator: 'orange',	message: __("Please input address")})
				return;
			}
			

			// const doc_workflow_state=$("textarea.web_customer_remark").attr("doc-workflow-state")
			// console.log(doc_workflow_state)
			// if (doc_workflow_state=="Draft"){
			// 	$('button.web_customer_remark').trigger("change", function() {console.log('in ch');shopping_cart.place_quotation_for_review(this)})
			// }
			// else{
			// 	shopping_cart.place_quotation_for_review(this);
			// }
			
			
		});
	},
	bind_place_order: function() {
		$(".btn-place-order").on("click", function() {
			shopping_cart.place_order(this);
		});
	},

	bind_request_quotation: function() {
		$('.btn-request-for-quotation').on('click', function() {
			shopping_cart.request_quotation(this);
		});
	},

	bind_change_qty: function() {
		// bind update button
		$(".cart-items").on("change", ".cart-qty", function() {
			var item_code = $(this).attr("data-item-code");
			var newVal = $(this).val();
			shopping_cart.shopping_cart_update({item_code, qty: newVal});
		});

		$(".cart-items").on('click', '.number-spinner button', function () {
			var btn = $(this),
				input = btn.closest('.number-spinner').find('input'),
				oldValue = input.val().trim(),
				newVal = 0;

			if (btn.attr('data-dir') == 'up') {
				newVal = parseInt(oldValue) + 1;
			} else {
				if (oldValue > 1) {
					newVal = parseInt(oldValue) - 1;
				}
			}
			input.val(newVal);

			let notes = input.closest("td").siblings().find(".notes").text().trim();
			var item_code = input.attr("data-item-code");
			shopping_cart.shopping_cart_update({
				item_code,
				qty: newVal,
				additional_notes: notes
			});
		});
	},

	bind_change_notes: function() {
		$('.cart-items').on('change', 'textarea', function() {
			const $textarea = $(this);
			const item_code = $textarea.attr('data-item-code');
			const qty = $textarea.closest('tr').find('.cart-qty').val();
			const notes = $textarea.val();
			shopping_cart.shopping_cart_update({
				item_code,
				qty,
				additional_notes: notes
			});
		});
	},

	bind_remove_cart_item: function() {
		$(".cart-items").on("click", ".remove-cart-item", (e) => {
			const $remove_cart_item_btn = $(e.currentTarget);
			var item_code = $remove_cart_item_btn.data("item-code");

			shopping_cart.shopping_cart_update({
				item_code: item_code,
				qty: 0
			});
		});
	},

	render_tax_row: function($cart_taxes, doc, shipping_rules) {
		var shipping_selector;
		if(shipping_rules) {
			shipping_selector = '<select class="form-control">' + $.map(shipping_rules, function(rule) {
				return '<option value="' + rule[0] + '">' + rule[1] + '</option>' }).join("\n") +
			'</select>';
		}

		var $tax_row = $(repl('<div class="row">\
			<div class="col-md-9 col-sm-9">\
				<div class="row">\
					<div class="col-md-9 col-md-offset-3">' +
					(shipping_selector || '<p>%(description)s</p>') +
					'</div>\
				</div>\
			</div>\
			<div class="col-md-3 col-sm-3 text-right">\
				<p' + (shipping_selector ? ' style="margin-top: 5px;"' : "") + '>%(formatted_tax_amount)s</p>\
			</div>\
		</div>', doc)).appendTo($cart_taxes);

		if(shipping_selector) {
			$tax_row.find('select option').each(function(i, opt) {
				if($(opt).html() == doc.description) {
					$(opt).attr("selected", "selected");
				}
			});
			$tax_row.find('select').on("change", function() {
				shopping_cart.apply_shipping_rule($(this).val(), this);
			});
		}
	},

	apply_shipping_rule: function(rule, btn) {
		return frappe.call({
			btn: btn,
			type: "POST",
			method: "webshop.webshop.shopping_cart.cart.apply_shipping_rule",
			args: { shipping_rule: rule },
			callback: function(r) {
				if(!r.exc) {
					shopping_cart.render(r.message);
				}
			}
		});
	},

	place_order: function(btn) {
		shopping_cart.freeze();

		return frappe.call({
			type: "POST",
			method: "webshop.webshop.shopping_cart.cart.place_order",
			btn: btn,
			callback: function(r) {
				if(r.exc) {
					shopping_cart.unfreeze();
					var msg = "";
					if(r._server_messages) {
						msg = JSON.parse(r._server_messages || []).join("<br>");
					}

					$("#cart-error")
						.empty()
						.html(msg || frappe._("Something went wrong!"))
						.toggle(true);
				} else {
					$(btn).hide();
					window.location.href = '/orders/' + encodeURIComponent(r.message);
				}
			}
		});
	},

	place_quotation_for_review: function(btn) {
		console.log(btn,'btn')
		shopping_cart.freeze();		
		const $btn = $(".btn-place-quotation-for-review");
		console.log($btn,'22')
		const doc_name = $btn.attr('data-doc-name');
		// const workflow_action= $btn.attr('data-workflow-action');
		const workflow_action=btn.getAttribute('data-workflow-action')
		console.log('doc_name',doc_name)
		return frappe.call({
			type: "POST",
			method: "sbl_webshop.overrides.place_quotation_for_review",
			args : {
				'doc_name' : doc_name,
				'workflow_action':workflow_action
			},
			callback: function(r) {
				if(r.exc) {
					shopping_cart.unfreeze();
					var msg = "";
					if(r._server_messages) {
						msg = JSON.parse(r._server_messages || []).join("<br>");
					}

					$("#cart-error")
						.empty()
						.html(msg || frappe._("Something went wrong!"))
						.toggle(true);
				} else {
					$(btn).hide();
					frappe.msgprint({
						title: __('Done'),
						indicator: 'green',
						message: __(r.message)
					})
					
					setTimeout(() => {
						if (workflow_action=='Submit For Review' || workflow_action=='Counter Offer') {
							location.reload()
							}
	
							if (workflow_action=='Reject' ) {
								window.location.href = '/all-products';
							}	
							let so=r.message
							if (so.startsWith('SO-') && workflow_action=='Accept') {
								window.location.href = '/orders/' + encodeURIComponent(r.message);						
							}						
					}, 1200);
								
					
				}
			}
		});
	},	
	request_quotation: function(btn) {
		shopping_cart.freeze();

		return frappe.call({
			type: "POST",
			method: "webshop.webshop.shopping_cart.cart.request_for_quotation",
			btn: btn,
			callback: function(r) {
				if(r.exc) {
					shopping_cart.unfreeze();
					var msg = "";
					if(r._server_messages) {
						msg = JSON.parse(r._server_messages || []).join("<br>");
					}

					$("#cart-error")
						.empty()
						.html(msg || frappe._("Something went wrong!"))
						.toggle(true);
				} else {
					$(btn).hide();
					window.location.href = '/quotations/' + encodeURIComponent(r.message);
				}
			}
		});
	},

	bind_coupon_code: function() {
		$(".bt-coupon").on("click", function() {
			shopping_cart.apply_coupon_code(this);
		});
	},

	apply_coupon_code: function(btn) {
		return frappe.call({
			type: "POST",
			method: "webshop.webshop.shopping_cart.cart.apply_coupon_code",
			btn: btn,
			args : {
				applied_code : $('.txtcoupon').val(),
				applied_referral_sales_partner: $('.txtreferral_sales_partner').val()
			},
			callback: function(r) {
				if (r && r.message){
					location.reload();
				}
			}
		});
	}
});

frappe.ready(function() {
	if (window.location.pathname === "/cart") {
		$(".cart-icon").hide();
	}
	shopping_cart.parent = $(".cart-container");
	shopping_cart.bind_events();
	$("input.web_customer_preferred_delivery_date").attr("min",moment().format('YYYY-MM-DD'))
});

function show_terms() {
	var html = $(".cart-terms").html();
	frappe.msgprint(html);
}

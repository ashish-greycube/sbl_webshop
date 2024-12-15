frappe.ready(function () {
    console.log(222)
    frappe.call('sbl_webshop.overrides.get_translations', {
     language: 'ar'
    }).then(r => {
     console.log(44,r.message)
     $.extend(frappe._messages, r.message);
    })
})
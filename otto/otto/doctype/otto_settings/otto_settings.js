// Copyright (c) 2024, Fabric and Contributers and contributors
// For license information, please see license.txt

frappe.ui.form.on("Otto Settings", {
	refresh(frm) {
        frappe.call({
            'method': "otto.app.prompt",
            callback: (r) => {
                //frm.refresh();
                console.log(r)
                
            }
        })
        
	},
});

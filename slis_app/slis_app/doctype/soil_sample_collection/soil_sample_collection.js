// Copyright (c) 2026, navaneeth and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Soil Sample Collection", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Soil Sample Collection", {
    refresh(frm) {

        console.log("App JS loaded");

        if (!frm.is_new() && frm.doc.docstatus === 0) {

            frm.add_custom_button(__('Add Sample'), function () {
                frappe.new_doc('Soil Sample Collection', {
                    client: frm.doc.client,
                    reference_name: frm.doc.reference_name
                });
            });

        }
    }
});



frappe.ui.form.on('Soil Sample Collection', {
    refresh: function(frm) {

        if (frappe.user.has_role("Senior Chemist")) {

            // When user clicks Assign To in sidebar
            $(document).on("click", ".add-assignment", function () {

                // Wait for dialog to render
                setTimeout(function () {

                    let dialog = $(".frappe-dialog:visible");

                    if (dialog.length) {

                        // Hide "Assign to me" checkbox
                        dialog.find("label:contains('Assign to me')")
                              .closest(".form-group")
                              .hide();

                    }

                }, 200);

            });

        }
    }
});



frappe.ui.form.on('Soil Sample Collection', {
    refresh: function(frm) {
        // Add the "Add to Register" button to the Actions menu
        frm.add_custom_button(__('Add to Register'), () => {
            create_register_from_list(frm.doc);
        }, __('Actions'));
    }
});

// Helper function to handle the data mapping
function create_register_from_list(doc) {
    frappe.model.with_doctype('Register', () => {
        // Create a new local instance of a Register document
        let new_reg = frappe.model.get_new_doc('Register');
        
        // --- MAPPING LOGIC ---
        // 'doc.name' is the ID of the current Soil Sample Collection record
        new_reg.source_sample_id = doc.name; 
        
        // Map other fields as needed
        new_reg.client = doc.client; // Example: mapping client name
        // new_reg.other_field = doc.other_field;

        // Redirect the user to the new Register form with the data pre-filled
        frappe.set_route('Form', 'Register', new_reg.name);
    });
}
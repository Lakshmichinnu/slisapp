# Copyright (c) 2026, navaneeth and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Sample ID"), "fieldname": "name", "fieldtype": "Link", "options": "Soil Sample Collection", "width": 150},
        {"label": _("Client Type"), "fieldname": "client_type", "fieldtype": "Data", "width": 120},
        {"label": _("Current Status"), "fieldname": "status", "fieldtype": "Data", "width": 180},
        {"label": _("Assignment Group"), "fieldname": "assignment_group", "fieldtype": "Data", "width": 150},
        {"label": _("Date of Collection"), "fieldname": "date_of_collection", "fieldtype": "Date", "width": 120}
    ]

    # Fetching records that are NOT 'With Research Assistant' and NOT 'Draft'
    samples = frappe.get_all("Soil Sample Collection", 
        fields=["name", "client_type", "status", "date_of_collection"],
        filters={
            "status": ["in", ["With Senior Chemist", "Draft", "With Assistant Director", "Enter File number"]]
        },
        order_by="date_of_collection desc"
    )

    data = []
    for sample in samples:
        data.append({
            "name": sample.name,
            "client_type": sample.client_type,
            "status": sample.status,
            "assignment_group": "Assignment Pending",  # Marking the group as requested
            "date_of_collection": sample.date_of_collection
        })

    return columns, data
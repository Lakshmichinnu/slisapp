# Copyright (c) 2026, navaneeth and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = [
        {"label": "Status Category", "fieldname": "status_category", "fieldtype": "Data", "width": 200},
        {"label": "Total Samples", "fieldname": "total_samples", "fieldtype": "html", "width": 150}
    ]

    # Count logic
    completed_count = frappe.db.count("Soil Sample Collection", filters={"status": "Completed"})
    pending_count = frappe.db.count("Soil Sample Collection", filters={
        "status": ["not in", ["Completed", "Draft"]]
    })

    # Create the clickable links
    completed_link = f'<a href="/app/soil-sample-collection?status=Completed"><b>{completed_count}</b></a>'
    pending_url = '/app/soil-sample-collection?status=["not in", ["Completed", "Draft"]]'
    pending_link = f'<a href=\'{pending_url}\'><b>{pending_count}</b></a>'

    data = [
        {"status_category": "Completed", "total_samples": completed_link},
        {"status_category": "Pending", "total_samples": pending_link}
    ]

    return columns, data
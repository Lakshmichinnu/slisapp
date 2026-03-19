# Copyright (c) 2026, navaneeth and contributors
# For license information, please see license.txt


import frappe

def execute(filters=None):
    # 1. Define columns with Serial Number and HTML for clickable counts
    columns = [
        {"label": "Sl. No", "fieldname": "idx", "fieldtype": "Int", "width": 80},
        {"label": "Type of Client", "fieldname": "client_type", "fieldtype": "Data", "width": 200},
        {"label": "Number of Samples", "fieldname": "sample_count", "fieldtype": "html", "width": 150}
    ]

    client_types = ["Farmer", "Consultancy", "Department"]
    data = []

    for i, client in enumerate(client_types, start=1):
        # 2. Count samples for each client type
        count = frappe.db.count("Soil Sample Collection", filters={"client_type": client})

        # 3. Generate the link to the list view filtered by client_type
        # Ensure the fieldname in the URL (client_type) matches your actual field name
        link = f'<a href="/app/soil-sample-collection?client_type={client}"><b>{count}</b></a>'

        data.append({
            "idx": i,
            "client_type": client,
            "sample_count": link
        })

    return columns, data
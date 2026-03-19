# Copyright (c) 2026, navaneeth and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    # Defining columns
    columns = [
        {"label": "Sl. No", "fieldname": "idx", "fieldtype": "Int", "width": 80},
        {"label": "Scheme Name", "fieldname": "scheme_name", "fieldtype": "Data", "width": 250},
        {"label": "Number of Samples", "fieldname": "sample_count", "fieldtype": "html", "width": 150}
    ]

    # 1. Dynamically fetch all unique scheme names from the database
    # We filter out empty/null values to keep the report clean
    schemes = frappe.get_all("Soil Sample Collection", 
        fields=["distinct scheme_name"], 
        filters={"scheme_name": ["not in", ["", None]]},
        order_by="scheme_name asc"
    )

    data = []

    for i, row in enumerate(schemes, start=1):
        scheme = row.scheme_name
        
        # 2. Count samples for this specific scheme
        count = frappe.db.count("Soil Sample Collection", filters={"scheme_name": scheme})

        # 3. Create the clickable link to the list view
        link = f'<a href="/app/soil-sample-collection?scheme_name={scheme}"><b>{count}</b></a>'

        data.append({
            "idx": i,
            "scheme_name": scheme,
            "sample_count": link
        })

    return columns, data
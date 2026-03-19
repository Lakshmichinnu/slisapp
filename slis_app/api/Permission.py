import frappe

def sample_permission_query(user=None):
    user = user or frappe.session.user
    roles = frappe.get_roles(user)

    # ADMIN / MD - Full access
    if user == "Administrator" or "Managing Director" in roles:
        return ""

    # Employee details fetch cheyyunnu
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        ["employment_type", "custom_lab_name", "custom_district_office_name"],
        as_dict=True
    )

    if not employee:
        return f"owner = '{user}'"

    conditions = []
    if employee.employment_type == "District Office":
        conditions.append("(client_type = 'Department')")
    #  Basic Permissions
    conditions.append(f"owner = '{user}'")
    conditions.append(f"(`_assign` LIKE '%%\"{user}\"%%')")

 # PSC OFFICER
    if "PSC Officer" in roles:
        conditions.append(
            "("
            "employee_type = 'Lab' "
            "OR (client_type = 'Department' "
            "AND status IN ('With PSC Officer', 'Returned to PSC Officer (Overload)'))"
            ")"
    )

    #  ASSISTANT DIRECTOR
    if "Assistant Director" in roles and employee.custom_district_office_name:
        conditions.append(
            f"(employee_type = 'District Office' "
            f"AND district_office_name = '{employee.custom_district_office_name}')"
        )

    #  SENIOR CHEMIST
    if "Senior Chemist" in roles and employee.custom_lab_name:
        conditions.append(
            f"(client_type = 'Department' "
            f"AND target_lab = '{employee.custom_lab_name}' "
            f"AND status IN ("
            f"'With Senior Chemist', "
            f"'Assigned to Research Assistant', "
            f"'Returned to Senior Chemist(Overload)', "
            f"'completed', "
            f"'cancelled'"
            f"))"
        )

    #  RESEARCH ASSISTANT
    if "Research Assistant" in roles and employee.custom_lab_name:
        conditions.append(
            f"(client_type = 'Department' "
            f"AND target_lab = '{employee.custom_lab_name}' "
            f"AND status IN ("
            f"'With Research Assistant', "
            f"'completed', "
            f"'cancelled', "
            f"'Returned to Senior Chemist(Overload)'"
            f"))"
        )

    #  FARMER / CONSULTANCY
 # FARMER / CONSULTANCY
    if employee.custom_lab_name and employee.employment_type != "District Office":
        conditions.append(
            f"(client_type IN ('Farmer', 'Consultancy') "
            f"AND lab_name = '{employee.custom_lab_name}')"
        )

    if conditions:
        return f"({' OR '.join(set(conditions))})"

    return ""
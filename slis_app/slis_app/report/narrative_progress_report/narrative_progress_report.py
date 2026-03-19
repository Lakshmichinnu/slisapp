import frappe
import calendar


# ======================================================
# REPORT ENTRY
# ======================================================

def execute(filters=None):

    filters = filters or {}

    # SESSION 1 DATA
    session1_columns = get_columns()
    session1_data = get_data(filters)

    # PROJECTS
    projects = frappe.db.sql("""
        SELECT DISTINCT project_name
        FROM `tabSoil Sample Collection`
        WHERE project_name IS NOT NULL AND project_name!=''
    """, as_dict=True)

    # SCHEMES
    schemes = frappe.db.sql("""
        SELECT DISTINCT scheme_name
        FROM `tabSoil Sample Collection`
        WHERE scheme_name IS NOT NULL AND scheme_name!=''
    """, as_dict=True)

    # SESSION 2
    session2_columns = get_session_two_columns(projects, schemes)
    session2_data = get_session_two_data(filters, projects, schemes)

    html = ""
    html += """
    <style>
    .scroll-container{
        overflow-x:auto;
        width:100%;
        border:1px solid #ddd;
        margin-bottom:20px;
    }

    .scroll-container::-webkit-scrollbar{
        height:10px;
    }

    .scroll-container::-webkit-scrollbar-track{
        background:#f1f1f1;
    }

    .scroll-container::-webkit-scrollbar-thumb{
        background:#4B8DF8;
        border-radius:5px;
    }

    .scroll-container::-webkit-scrollbar-thumb:hover{
        background:#2f6de0;
    }

    .table{
        white-space:nowrap;
    }
    </style>
    """

    # ======================================================
    # TABLE 1 : NARRATIVE PROGRESS REPORT
    # ======================================================

    html += "<h3>Narrative Progress Report</h3>"
    html += "<div class='scroll-container'><table class='table table-bordered'>"

    html += "<thead><tr>"
    for col in session1_columns:
        html += f"<th>{col['label']}</th>"
    html += "</tr></thead><tbody>"

    for row in session1_data:
        html += "<tr>"
        for col in session1_columns:
            val = row.get(col["fieldname"], "")
            html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"


    # ======================================================
    # TABLE 2 : CONSOLIDATED PENDING WORK
    # ======================================================

    html += "<br><h3>Consolidated Pending Work</h3>"
    html += "<div class='scroll-container'><table class='table table-bordered'>"

    html += "<thead><tr>"
    html += "<th>Laboratory</th>"

    for col in session2_columns:
        html += f"<th>{col['label']}</th>"

    html += "</tr></thead><tbody>"

    for row in session2_data:

        html += "<tr>"

        html += f"<td>{row.get('lab_name','')}</td>"

        for col in session2_columns:

            val = row.get(col["fieldname"], 0)

            html += f"<td>{val}</td>"

        html += "</tr>"

    html += "</tbody></table></div>"


    # ======================================================
    # MESSAGE
    # ======================================================

    month = int(filters.get("month"))
    year = int(filters.get("year"))

    month_name = calendar.month_name[month]

    financial_year, fy_start, fy_end = get_financial_year_range(month, year)

    message = f"Samples Analysed in the Month of {month_name} {financial_year}<br><br>{html}"

    return [], [], message


def get_dm(lab, month, year):

    result = frappe.db.sql("""

        SELECT COUNT(name)

        FROM `tabSoil Sample Collection`

        WHERE
        status='completed'
        AND MONTH(completed_date)=%s
        AND YEAR(completed_date)=%s

        AND (
            (client_type='Department' AND target_lab=%s)
            OR
            (client_type IN ('Farmer','Consultancy') AND lab_name=%s)
        )

    """, (month, year, lab, lab))

    return result[0][0] if result else 0
def get_pt(lab, fy_start, month_end):

    result = frappe.db.sql("""

        SELECT COUNT(name)

        FROM `tabSoil Sample Collection`

        WHERE
        status='completed'
        AND completed_date BETWEEN %s AND %s

        AND (
            (client_type='Department' AND target_lab=%s)
            OR
            (client_type IN ('Farmer','Consultancy') AND lab_name=%s)
        )

    """, (fy_start, month_end, lab, lab))

    return result[0][0] if result else 0

def get_pending(lab, fy_start, month_end):

    assigned = frappe.db.sql("""

        SELECT COUNT(name)

        FROM `tabSoil Sample Collection`

        WHERE
        (
            (client_type='Department' AND target_lab=%s)
            OR
            (client_type IN ('Farmer','Consultancy') AND lab_name=%s)
        )

        AND creation BETWEEN %s AND %s

    """, (lab, lab, fy_start, month_end))[0][0] or 0


    completed = frappe.db.sql("""

        SELECT COUNT(name)

        FROM `tabSoil Sample Collection`

        WHERE
        (
            (client_type='Department' AND target_lab=%s)
            OR
            (client_type IN ('Farmer','Consultancy') AND lab_name=%s)
        )

        AND status='completed'
        AND completed_date BETWEEN %s AND %s

    """, (lab, lab, fy_start, month_end))[0][0] or 0


    return assigned - completed

# ======================================================
# FINANCIAL YEAR
# ======================================================

def get_financial_year_range(month, year):

    if month >= 4:

        fy_start = f"{year}-04-01"
        fy_end = f"{year+1}-03-31"
        financial_year = f"{year}-{year+1}"

    else:

        fy_start = f"{year-1}-04-01"
        fy_end = f"{year}-03-31"
        financial_year = f"{year-1}-{year}"

    return financial_year, fy_start, fy_end


# ======================================================
# MONTH END
# ======================================================

def get_month_end_date(month, year):

    last_day = calendar.monthrange(year, month)[1]

    return f"{year}-{month:02d}-{last_day}"


# ======================================================
# SESSION 1 COLUMNS
# ======================================================

def get_columns():

    return [

        {"label": "Laboratory Name", "fieldname": "lab_name", "fieldtype": "Data", "width": 220},

        {"label": "Profile Target", "fieldname": "profile_target", "fieldtype": "Int", "width": 130},

        {"label": "Other Target", "fieldname": "other_target", "fieldtype": "Int", "width": 130},

        {"label": "Total Target", "fieldname": "target", "fieldtype": "Int", "width": 120},

        {"label": "DM (During Month)", "fieldname": "dm", "fieldtype": "Int", "width": 160},

        {"label": "PT (Progressive Total)", "fieldname": "pt", "fieldtype": "Int", "width": 170},

        {"label": "Pending", "fieldname": "pending", "fieldtype": "Int", "width": 140}

    ]


# ======================================================
# LAB ACCESS
# ======================================================

def get_labs():

    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "Senior Chemist" in roles:

        emp = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            ["custom_lab_name"],
            as_dict=True
        )

        if emp and emp.custom_lab_name:
            return [emp.custom_lab_name]

        return []

    elif "PSC Officer" in roles or "Administrator" in roles or "Managing Director" in roles:

        return frappe.get_all("Soil Laboratory", pluck="name")

    return []


# ======================================================
# TARGET
# ======================================================

def get_target(lab, month, financial_year):

    r = frappe.db.sql("""
        SELECT
        SUM(mt.profile_sample_count * lt.ra_count) AS profile_target,
        SUM(mt.other_sample_count * lt.ra_count) AS other_target
        FROM `tabMonthly Target` mt
        INNER JOIN `tabLab Target` lt ON lt.parent = mt.name
        WHERE lt.lab_name=%s AND lt.month=%s AND mt.financial_year=%s
    """,(lab,month,financial_year),as_dict=True)

    if r:
        p = r[0]["profile_target"] or 0
        o = r[0]["other_target"] or 0
        return {"profile":p,"other":o,"total":p+o}

    return {"profile":0,"other":0,"total":0}


# ======================================================
# SESSION 1 DATA
# ======================================================

def get_data(filters):

    month = int(filters.get("month"))
    year = int(filters.get("year"))

    month_name = calendar.month_name[month]

    financial_year, fy_start, fy_end = get_financial_year_range(month, year)

    month_end = get_month_end_date(month, year)

    labs = get_labs()

    data=[]

    for lab in labs:

        t = get_target(lab,month_name,financial_year)

        dm = get_dm(lab, month, year)

        pt = get_pt(lab, fy_start, month_end)

        pending = get_pending(lab, fy_start, month_end)

        data.append({

            "lab_name":lab,
            "profile_target":t["profile"],
            "other_target":t["other"],
            "target":t["total"],
            "dm":dm,
            "pt":pt,
            "pending":pending

        })

    return data


# ======================================================
# SESSION 2 COLUMNS
# ======================================================

def get_session_two_columns(projects, schemes):

    cols = [

        {"label": "Farmer", "fieldname": "farmer", "fieldtype": "Int", "width": 120},

        {"label": "Consultancy", "fieldname": "consultancy", "fieldtype": "Int", "width": 120},

        {"label": "Campaign", "fieldname": "campaign", "fieldtype": "Int", "width": 120},

        {"label": "Routine Research", "fieldname": "routine", "fieldtype": "Int", "width": 150}

    ]

    for p in projects:

        name = p.project_name.replace(" ","_").lower()

        cols.append({"label":f"{p.project_name} Profile","fieldname":f"{name}_profile","fieldtype":"Int","width":130})
        cols.append({"label":f"{p.project_name} Surface","fieldname":f"{name}_surface","fieldtype":"Int","width":130})
        cols.append({"label":f"{p.project_name} Micro","fieldname":f"{name}_micro","fieldtype":"Int","width":130})

    for s in schemes:

        name = s.scheme_name.replace(" ","_").lower()

        cols.append({"label":f"{s.scheme_name} Profile","fieldname":f"{name}_profile_s","fieldtype":"Int","width":130})
        cols.append({"label":f"{s.scheme_name} Surface","fieldname":f"{name}_surface_s","fieldtype":"Int","width":130})
        cols.append({"label":f"{s.scheme_name} Micro","fieldname":f"{name}_micro_s","fieldtype":"Int","width":130})

    cols.append({"label":"Total Pending","fieldname":"total_pending","fieldtype":"Int","width":150})

    return cols

def get_session_two_data(filters, projects, schemes):

    labs = get_labs()

    samples = frappe.db.sql("""
        SELECT
            lab_name,
            target_lab,
            client_type,
            project_name,
            scheme_name,
            profile_sample,
            surface_sample,
            micro_sample
        FROM `tabSoil Sample Collection`
        WHERE status != 'completed'
    """, as_dict=True)

    data = []

    for lab in labs:

        row = {"lab_name": lab}
        total = 0

        farmer = 0
        consultancy = 0

        # Initialize project columns
        for p in projects:

            if not p.project_name:
                continue

            fname = p.project_name.replace(" ", "_").lower()

            row[f"{fname}_profile"] = 0
            row[f"{fname}_surface"] = 0
            row[f"{fname}_micro"] = 0

        # Initialize scheme columns
        for s in schemes:

            if not s.scheme_name:
                continue

            fname = s.scheme_name.replace(" ", "_").lower()

            row[f"{fname}_profile_s"] = 0
            row[f"{fname}_surface_s"] = 0
            row[f"{fname}_micro_s"] = 0

        for sample in samples:

            sample_lab = sample.target_lab if sample.client_type == "Department" else sample.lab_name

            if sample_lab != lab:
                continue

            # Farmer / Consultancy
            if sample.client_type == "Farmer":
                farmer += 1

            elif sample.client_type == "Consultancy":
                consultancy += 1

            # -----------------------------
            # PROJECT SAMPLE COUNT
            # -----------------------------
            if sample.project_name:

                fname = sample.project_name.replace(" ", "_").lower()

                if sample.profile_sample and f"{fname}_profile" in row:
                    row[f"{fname}_profile"] += 1
                    total += 1

                if sample.surface_sample and f"{fname}_surface" in row:
                    row[f"{fname}_surface"] += 1
                    total += 1

                if sample.micro_sample and f"{fname}_micro" in row:
                    row[f"{fname}_micro"] += 1
                    total += 1

            # -----------------------------
            # SCHEME SAMPLE COUNT
            # -----------------------------
            if sample.scheme_name:

                fname = sample.scheme_name.replace(" ", "_").lower()

                if sample.profile_sample and f"{fname}_profile_s" in row:
                    row[f"{fname}_profile_s"] += 1
                    total += 1

                if sample.surface_sample and f"{fname}_surface_s" in row:
                    row[f"{fname}_surface_s"] += 1
                    total += 1

                if sample.micro_sample and f"{fname}_micro_s" in row:
                    row[f"{fname}_micro_s"] += 1
                    total += 1

        row["farmer"] = farmer
        row["consultancy"] = consultancy
        row["campaign"] = 0
        row["routine"] = 0

        total += farmer + consultancy

        row["total_pending"] = total

        data.append(row)

    return data
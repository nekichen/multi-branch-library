{
    "name": "Library Reporting",
    "description": """Library Reporting is an app for managing library loans report.""",
    "category": "Addons",
    "author": "Naura",
    "depends": ["web", "mail", "base", "multi_branch_library_management", "multi_branch_book_loan_management"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/library_book_report.xml",
        "views/library_book_template.xml",
        "views/library_loan_report.xml",
        "views/library_loan_template.xml",
        "views/library_report.xml",
        ],
    "installable": True,
}
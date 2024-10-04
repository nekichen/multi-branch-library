{
    "name": "Library Loan Management",
    "description": """Library is an app for managing library loans.""",
    "category": "Addons",
    "author": "Naura",
    "depends": ["web", "mail", "base", "multi_branch_library_management"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/library_book_inherit_view.xml",
        "views/library_loan_view.xml",
        "views/library_loan_menu.xml",
        ],
    "installable": True,
}
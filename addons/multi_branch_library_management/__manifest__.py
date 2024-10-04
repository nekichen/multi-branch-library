{
    "name": "Library Book Management",
    "description": """Library is an app for managing library books.""",
    "category": "Addons",
    "author": "Naura",
    "depends": ["web", "mail", "base"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/library_book_view.xml",
        "views/library_book_menu.xml",
        ],
    "installable": True,
}
"""
Contains a list of important locations to calculate distances from properties.
These locations represent key necessities for daily life.
"""

LOCATIONS = {
    "work": [
        "Wynard Station Sydney, NSW",  # Major business district
    ],
    "groceries": [
        "Woolworths",  # Will be appended with suburb from property
        "Coles",       # Will be appended with suburb from property
        "Aldi",        # Will be appended with suburb from property
        "IGA"         # Will be appended with suburb from property
    ],
    "schools": [
        "Sydney Grammar School, College Street, Darlinghurst",
    ]
} 
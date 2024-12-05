# -*- coding: utf-8 -*-
{
    'name': "course_ecommerce",
    'summary': """
        """,
    'description': """
        
    """,
    'author': "Alejandro Martínez",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account', 'sale_management', 'website', 'website_sale', 'crm'],
    'data': [
        'security/curse_security.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/curse_views.xml',
        'views/curse_student_views.xml',
        'views/curse_student_note_views.xml',
        'views/website_menus.xml',
    ],

    'installable': True,
    'application': True,
    
}

from odoo import models, fields, api
from datetime import date
import re


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    parent_id = fields.Many2one('product.template', string='Producto Padre')
    date_start = fields.Date(string='Fecha de Inicio')
    date_end = fields.Date(string='Fecha de Fin')
    tutor_id = fields.Many2one('res.partner', string='Tutor')
    xtec = fields.Selection([
        ('si', 'SÍ'),
        ('no', 'NO'),
        ('temporal', 'TEMPORAL')
    ], string='XTEC')
    external_id = fields.Char(string='External ID')

    @api.model
    def publish_courses(self):
        today = date.today()
        courses = self.search([('date_start', '<=', today), ('date_end', '>=', today), ('website_published', '=', False)])
        for course in courses:
            course.write({'website_published': True})

    @api.model
    def update_product_prices(self):
        products = self.search([])
        for product in products:
            match = re.search(r'-\s*(\d+)\s*€', product.name)
            if match:
                price = float(match.group(1))
                product.write({'list_price': price})

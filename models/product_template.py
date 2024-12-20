from odoo import models, fields

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

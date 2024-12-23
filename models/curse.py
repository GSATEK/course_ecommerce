from odoo import models, fields, api

class Curse(models.Model):
    _name = 'curse'
    _inherit = ['mail.thread']

    name = fields.Char(compute='_compute_name', store=True, string='Nombre')
    product_id = fields.Many2one('product.template', domain="[('parent_id', '=', False)]", string='Producto')
    line_student_ids = fields.One2many('curse.student', 'curse_id', string='Estudiantes')
    tutor_id = fields.Many2one('res.partner', related='product_id.tutor_id', string='Tutor')
    @api.depends('product_id', 'product_id.date_start', 'product_id.date_end')
    def _compute_name(self):
        for record in self:
            if record.product_id:
                record.name = f"{record.product_id.name} ({record.product_id.date_start} - {record.product_id.date_end})"
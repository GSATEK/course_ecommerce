from odoo import models, fields, api

class Curse(models.Model):
    _name = 'curse'
    _inherit = ['mail.thread']

    name = fields.Char(compute='_compute_name', store=True, string='Nombre')
    product_id = fields.Many2one('product.template', domain="[('parent_id', '=', False)]", string='Producto')
    line_student_ids = fields.Many2many('curse.student', 'curse_student_rel', 'curse_id', 'student_id', string='Estudiantes', ondelete='cascade')
    tutor_id = fields.Many2one('res.partner', related='product_id.tutor_id', string='Tutor')
    date_start = fields.Date(string='Fecha de Inicio')
    date_end = fields.Date(string='Fecha de Fin')
    student_count = fields.Integer(string='Número de Estudiantes', compute='_compute_student_count')


    @api.depends('product_id', 'product_id.date_start', 'product_id.date_end')
    def _compute_name(self):
        for record in self:
            if record.product_id:
                record.name = f"{record.product_id.name} ({record.product_id.date_start} - {record.product_id.date_end})"

    @api.depends('line_student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.line_student_ids)

    def action_view_students(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Estudiantes',
            'view_mode': 'tree,form',
            'res_model': 'curse.student',
            'domain': [('curse_ids', '=', self.id)],
            'context': "{'create': False}"
        }
from odoo import models, fields, api

class CurseStudent(models.Model):
    _name = 'curse.student'
    _inherit = ['mail.thread']

    res_partner = fields.Many2one('res.partner', string='Estudiante')
    registration_date = fields.Date(string='Fecha de Inscripción')
    note_ids = fields.One2many('curse.student.note', 'student_id', string='Notas')
    grade_average = fields.Float(compute='_compute_grade_average', string='Promedio de Notas')
    curse_ids = fields.Many2many('curse', 'curse_student_rel', 'student_id', 'curse_id', string='Cursos', ondelete='cascade')
    name = fields.Char(compute='_compute_name', store=True, string='Nombre del Estudiante')
    specialty = fields.Char(string='Especialidad')
    course_count = fields.Integer(string='Course Count', compute='_compute_course_count')
    note_count = fields.Integer(string='Note Count', compute='_compute_note_count')
    image_1920 = fields.Image(string='Image')
    order_ids = fields.One2many('sale.order', 'partner_id', string='Pedidos', compute='_compute_order_ids')
    order_count = fields.Integer(string='Order Count', compute='_compute_order_count')
    currency_id = fields.Many2one('res.currency', string='Currency')
    total_invoiced = fields.Monetary(string='Total Invoiced', compute='_compute_total_invoiced', currency_field='currency_id')

    @api.depends('res_partner')
    def _compute_name(self):
        for record in self:
            record.name = record.res_partner.name if record.res_partner else ''

    @api.depends('note_ids.nota')
    def _compute_grade_average(self):
        for record in self:
            total = sum(note.nota for note in record.note_ids)
            count = len(record.note_ids)
            record.grade_average = total / count if count > 0 else 0

    @api.depends('curse_ids')
    def _compute_course_count(self):
        for student in self:
            student.course_count = len(student.curse_ids)

    def action_view_courses(self):
        self.ensure_one()
        if self.course_count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Curso',
                'res_model': 'curse',
                'view_mode': 'form',
                'res_id': self.curse_ids.id,
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cursos',
                'res_model': 'curse',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.curse_ids.ids)],
            }

    @api.depends('note_ids')
    def _compute_note_count(self):
        for student in self:
            student.note_count = len(student.note_ids)

    def action_view_notes(self):
        self.ensure_one()
        if self.note_count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Nota',
                'res_model': 'curse.student.note',
                'view_mode': 'form',
                'res_id': self.note_ids.id,
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Notas',
                'res_model': 'curse.student.note',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.note_ids.ids)],
            }

    @api.depends('res_partner')
    def _compute_order_count(self):
        for student in self:
            student.order_count = self.env['sale.order'].search_count([('partner_id', '=', student.res_partner.id)])
    def action_view_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedidos',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.res_partner.id)],
        }

    @api.depends('res_partner')
    def _compute_order_ids(self):
        for student in self:
            student.order_ids = self.env['sale.order'].search([('partner_id', '=', student.res_partner.id)])

    @api.depends('res_partner')
    def _compute_total_invoiced(self):
        for student in self:
            invoices = self.env['account.move'].search(
                [('partner_id', '=', student.res_partner.id), ('state', '=', 'posted'),
                 ('move_type', '=', 'out_invoice')])
            student.total_invoiced = sum(invoice.amount_total for invoice in invoices)

    def action_view_invoiced_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturado',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.res_partner.id), ('invoice_status', '=', 'invoiced')],
        }
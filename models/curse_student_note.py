from odoo import models, fields, api

class CurseStudentNote(models.Model):
    _name = 'curse.student.note'
    _inherit = ['mail.thread']

    name = fields.Char(string='Nombre')
    nota = fields.Float(string='Nota')
    student_id = fields.Many2one('curse.student', string='Estudiante')
    student_name = fields.Char(string='Nombre del Estudiante', compute='_compute_student_name')

    @api.depends('student_id')
    def _compute_student_name(self):
        for record in self:
            record.student_name = record.student_id.res_partner.name if record.student_id else ''
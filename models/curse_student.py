from odoo import models, fields, api

class CurseStudent(models.Model):
    _name = 'curse.student'
    _inherit = ['mail.thread']

    res_partner = fields.Many2one('res.partner', string='Estudiante')
    registration_date = fields.Date(string='Fecha de Inscripción')
    note_ids = fields.One2many('curse.student.note', 'student_id', string='Notas')
    grade_average = fields.Float(compute='_compute_grade_average', string='Promedio de Notas')
    curse_id = fields.Many2one('curse', string='Curso')

    @api.depends('note_ids.nota')
    def _compute_grade_average(self):
        for record in self:
            total = sum(note.nota for note in record.note_ids)
            count = len(record.note_ids)
            record.grade_average = total / count if count > 0 else 0
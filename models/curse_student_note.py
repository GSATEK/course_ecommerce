from odoo import models, fields

class CurseStudentNote(models.Model):
    _name = 'curse.student.note'

    name = fields.Char(string='Nombre')
    nota = fields.Float(string='Nota')
    student_id = fields.Many2one('curse.student', string='Estudiante')
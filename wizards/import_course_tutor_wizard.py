from odoo import models, fields, api
import base64
import xlrd
from datetime import datetime

class ImportCourseTutorWizard(models.TransientModel):
    _name = 'import.course.tutor.wizard'
    _description = 'Wizard for importing courses and tutors'

    file = fields.Binary(string='Archivo', required=True)
    filename = fields.Char(string='Nombre del Archivo')

    def import_courses_tutors(self):
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        for row in range(1, sheet.nrows):
            external_id = sheet.cell(row, 0).value
            name = sheet.cell(row, 1).value
            date_start = sheet.cell(row, 2).value
            date_end = sheet.cell(row, 3).value
            xtec = sheet.cell(row, 4).value
            comment = sheet.cell(row, 5).value
            tutor_name = sheet.cell(row, 6).value

            # Convertir las fechas al formato correcto o a None si están vacías
            date_start = datetime.strptime(date_start, '%d.%m.%Y').strftime('%Y-%m-%d') if date_start else None
            date_end = datetime.strptime(date_end, '%d.%m.%Y').strftime('%Y-%m-%d') if date_end else None

            product = self.env['product.template'].create({
                'name': name,
                'date_start': date_start,
                'date_end': date_end,
                'tutor_id': self.env['res.partner'].search([('name', '=', tutor_name)], limit=1).id,
                'xtec': xtec,
                'external_id': external_id,
            })
            course = self.env['curse'].create({
                'name': name,
                'product_id': product.id,
            })
            course.message_post(body=comment)
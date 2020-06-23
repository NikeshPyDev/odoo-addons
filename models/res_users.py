
from odoo import api, fields, models
import uuid



class Users(models.Model):
    _inherit = "res.users"

    access_token = fields.Text(string="Access Token")

    def generate_access_token(self):
        self.access_token = str(uuid.uuid4())
        return self.access_token


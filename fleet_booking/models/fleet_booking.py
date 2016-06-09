# -*- coding: utf-8 -*-

from openerp import api, fields, models


# INHERITED MODELS

class HrDepartment(models.Model):

    _name = "fleet_booking.branch"
    _inherit = 'hr.department'

    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')


class Person(models.Model):

    _inherit = 'res.partner'

    id_type = fields.Selection(
        [(u'National Id', u'National Id'), (u'Iqama', u'Iqama'),
         (u'Passport', u'Passport')],
        string='ID Type',
        )
    issuer = fields.Char(string='Issuer string')
    issuer_date = fields.Date(string='Date of Issue')
    license_type = fields.Selection([(u'Private', u'Private'),
                                     (u'General', u'General'),
                                     (u'International', u'International')],
                                    string='License Type')
    license_number = fields.Char(string='License Number')
    license_expiry_date = fields.Date(string='License Expiry Date')
    third_name = fields.Char(string='Third Name')
    family_name = fields.Char(string='Family Name')

    def check_age(self, cr, uid, ids, context=None, parent=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.customer and r.birthdate_date and r.age < 21:
                return False
        return True

    _constraints = [
        (check_age, 'Age restriction. Person must be elder than 20.', ['birthdate_date']),
    ]


class FleetBranch(models.Model):

    _inherit = 'fleet.vehicle'

    branch = fields.Many2one('fleet_booking.branch')


class Fleet(models.Model):

    _inherit = 'fleet.vehicle'

    colour = fields.Selection([('black', 'Black'),
                              ('blue', 'Blue'),
                              ('red', 'Red'),
                              ('white', 'White'),
                              ('sliver', 'Sliver'),
                              ('yellow', 'Yellow'),
                              ('green', 'Green'),
                              ('gold', 'Gold'),
                              ('orange', 'Orange'),
                              ('brown', 'Brown'),
                              ], string='Color', default='black')
    model_year = fields.Integer('Model Year')
    daily_rate = fields.Float('Daily Rate')
    extra_rate = fields.Float('Rate per extra km')
    allowed_per_day = fields.Float('Allowed km per day')
    paid = fields.Float('Paid amount')
    remain = fields.Float('Remaining amount')
    reg_expiry = fields.Date('Registration expiry')
    ins_expiry = fields.Date('Insurance expiry')
    next_maintain = fields.Date('Next maintenance')
    payments_ids = fields.One2many('fleet_booking.payments', 'fleet_vehicle_id', string='Payments')
    insurance_ids = fields.One2many('fleet_booking.insurances', 'fleet_vehicle_id', string='Insurance Installments')
    deprecation_ids = fields.One2many('fleet_booking.deprecation', 'fleet_vehicle_id', string='Vehicle Depreciation')
    # TODO Rename deprecation to depreciation


class Service(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    state = fields.Selection([('draft', 'Draft'),
                              ('request', 'Request'),
                              ('done', 'Done'),
                              ('paid', 'Paid')],
                             string='State', default='draft')
    account_invoice_ids = fields.One2many('account.invoice', 'fleet_vehicle_log_services_ids', string='Invoices', copy=False)
    cost_subtype_in_branch = fields.Boolean(related='cost_subtype_id.in_branch')

    @api.multi
    def submit(self):
        in_shop_vehicle_state = self.env['fleet.vehicle.state'].browse(1)
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        vehicle.state_id = in_shop_vehicle_state
        self.write({'state': 'request'})

    @api.multi
    def confirm(self):
        active_vehicle_state = self.env['fleet.vehicle.state'].browse(2)
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        vehicle.state_id = active_vehicle_state
        self.write({'state': 'done'})

    @api.multi
    def approve(self):
        self.write({'state': 'paid'})


class ServiceType(models.Model):
    _inherit = 'fleet.service.type'

    in_branch = fields.Boolean(default=False, readonly=True, invisible=True)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fleet_vehicle_log_services_ids = fields.Many2one('fleet.vehicle.log.services')

# OWN MODELS

class Payments(models.Model):
    _name = 'fleet_booking.payments'
    _order = 'fleet_vehicle_id, sequence, id'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    sequence = fields.Integer(default=1,
                              help="Gives the sequence of this line when displaying the vehicle.")
    payment_date = fields.Datetime(string='Date', default=fields.Datetime.now())
    amount = fields.Float(string='Amount')


class InsuranceInstallments(models.Model):
    _name = 'fleet_booking.insurances'
    _order = 'fleet_vehicle_id, sequence, id'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    sequence = fields.Integer(default=1,
                              help="Gives the sequence of this line when displaying the vehicle.")
    insurance_date = fields.Datetime(string='Date', default=fields.Datetime.now())
    amount = fields.Float(string='Amount')


class VehicleDepreciation(models.Model):
    _name = 'fleet_booking.deprecation'
    _order = 'fleet_vehicle_id, sequence, id'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    sequence = fields.Integer(default=1,
                              help="Gives the sequence of this line when displaying the vehicle.")
    deprecation_date = fields.Datetime(string='Date', default=fields.Datetime.now())
    amount = fields.Float(string='Amount')

    # @api.one
    # @api.depends('payment_date')
    # def get_serial_num(self):
    #    print '# :',    self._context.get('active_ids', []) or []
    #    print '# :',    self._context.get('active_id', []) or []

    # @api.model
    # def default_get(self, fields_list):
    #     defaults = super(Payments, self).default_get(fields_list)
    #     res = self.env['fleet_booking.payments'].search(
    #         [('fleet_vehicle_id', '=', self.fleet_vehicle_id)],
    #         limit=1, order='serial_num ASC')
    #     if res:
    #         defaults.setdefault('serial_num', res.serial_num + 1)
    #     return defaults

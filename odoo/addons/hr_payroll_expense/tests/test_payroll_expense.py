# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.hr_payroll.tests.common import TestPayslipBase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestPayrollExpense(TestPayslipBase):

    def test_expense_in_payroll_payment_state(self):
        product_a = self.env['product.product'].create({
            'name': 'test',
            'list_price': 100,
        })
        richard_partner_id = self.env['res.partner'].create({'name': 'Richard', 'phone': '21454', 'type': 'private'}).id
        richard_bank_account = self.env['res.partner.bank'].create({
            'acc_number': "0123456789",
            'partner_id': richard_partner_id,
            'acc_type': 'bank',
        })
        self.richard_emp.write({
            'address_id': richard_partner_id,
            'address_home_id': richard_partner_id,
            'bank_account_id': richard_bank_account.id,
        })
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Test Expenses',
            'employee_id': self.richard_emp.id,
            'accounting_date': '2018-01-02',
            'expense_line_ids': [(0, 0, {
                'name': 'Expense line',
                'employee_id': self.richard_emp.id,
                'product_id': product_a.id,
                'unit_amount': 100.00,
            })]
        })
        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_report_in_next_payslip()

        self.richard_emp.contract_ids[0].state = 'open'

        payslip = self.env['hr.payslip'].create({
            'name': 'Payslip',
            'employee_id': self.richard_emp.id,
        })


        payslip.write({'expense_sheet_ids': expense_sheet.ids})
        payslip.compute_sheet()
        payslip.action_payslip_done()

        # Verify that the payslip is in done state
        self.assertEqual(payslip.state, 'done', 'State not changed!')

        # Click on the 'Mark as paid' button on payslip
        payslip.action_payslip_paid()

        # Verify that the payslip is in paid state
        self.assertEqual(payslip.state, 'paid', 'State not changed!')

        # Verify expense is paid as well
        self.assertEqual(expense_sheet.payment_state, 'paid', 'Expense not paid in payslip')

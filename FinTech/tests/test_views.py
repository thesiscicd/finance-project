from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from FinTech.models import Account, Income, Expense, IncomeCategory, ExpenseCategory
from datetime import date

class ViewsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
        )

        # Create an account for the user
        self.account = Account.objects.create(
            user=self.user, balance=1000, name="Test Account", details="Test Details"
        )

        # Create categories
        self.income_category = IncomeCategory.objects.create(user=self.user, name="Salary")
        self.expense_category = ExpenseCategory.objects.create(user=self.user, name="Food")

        # Create Income and Expense records
        self.income = Income.objects.create(
            user=self.user,
            name="Test Income",
            category=self.income_category,
            amount=500,
            date=date.today(),
            note="Test income note",
        )
        self.expense = Expense.objects.create(
            user=self.user,
            name="Test Expense",
            category=self.expense_category,
            amount=200,
            date=date.today(),
            note="Test expense note",
        )

        # Login the test client
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertIn("balance", response.context)

    def test_income_view(self):
        response = self.client.get(reverse("incomes"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "income.html")
        self.assertIn("categories", response.context)

    def test_add_income(self):
        response = self.client.post(
            reverse("incomes"),
            {
                "name": "New Income",
                "category": self.income_category.id,
                "amount": 300,
                "date": date.today(),
                "note": "New income note",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertTrue(Income.objects.filter(name="New Income").exists())

    def test_expenses_view(self):
        response = self.client.get(reverse("expenses"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expense.html")
        self.assertIn("categories", response.context)

    def test_add_expense(self):
        response = self.client.post(
            reverse("expenses"),
            {
                "name": "New Expense",
                "category": self.expense_category.id,
                "amount": 150,
                "date": date.today(),
                "note": "New expense note",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertTrue(Expense.objects.filter(name="New Expense").exists())

    def test_delete_income(self):
        response = self.client.post(reverse("delete-income", args=[self.income.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertFalse(Income.objects.filter(id=self.income.id).exists())

    def test_delete_expense(self):
        response = self.client.post(reverse("delete-expense", args=[self.expense.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertFalse(Expense.objects.filter(id=self.expense.id).exists())

    def test_edit_income(self):
        response = self.client.post(
            reverse("edit-income", args=[self.income.id]),
            {
                "name": "Updated Income",
                "category": self.income_category.id,
                "amount": 700,
                "date": date.today(),
                "note": "Updated income note",
            },
        )
        self.assertEqual(response.status_code, 302)
        updated_income = Income.objects.get(id=self.income.id)
        self.assertEqual(updated_income.name, "Updated Income")
        self.assertEqual(updated_income.amount, 700)

    def test_edit_expense(self):
        response = self.client.post(
            reverse("edit-expense", args=[self.expense.id]),
            {
                "name": "Updated Expense",
                "category": self.expense_category.id,
                "amount": 100,
                "date": date.today(),
                "note": "Updated expense note",
            },
        )
        self.assertEqual(response.status_code, 302)
        updated_expense = Expense.objects.get(id=self.expense.id)
        self.assertEqual(updated_expense.name, "Updated Expense")
        self.assertEqual(updated_expense.amount, 100)

    def test_report_generation(self):
        response = self.client.get(reverse("expense-report", args=["weekly"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

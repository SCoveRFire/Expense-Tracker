import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Определяем путь к файлу данных в той же папке, где находится программа
DATA_FILE = os.path.join(os.path.dirname(__file__), "expenses.json")

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x500")

        self.expenses = []
        self.load_data()

        # Поля ввода
        tk.Label(root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(root, textvariable=self.category_var,
                                           values=["Еда", "Транспорт", "Развлечения", "Другое"])
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        self.add_btn = tk.Button(root, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=5, pady=5)

        # Таблица расходов
        columns = ("Дата", "Категория", "Сумма")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.grid(row=1, column=0, columnspan=7, padx=5, pady=5)

        # Фильтры
        filter_frame = tk.Frame(root)
        filter_frame.grid(row=2, column=0, columnspan=7, pady=5)

        tk.Label(filter_frame, text="Фильтр по категории:").pack(side=tk.LEFT, padx=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Другое"])
        self.filter_category.set("Все")
        self.filter_category.pack(side=tk.LEFT, padx=5)

        tk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").pack(side=tk.LEFT, padx=5)
        self.filter_date_from = tk.Entry(filter_frame, width=12)
        self.filter_date_from.pack(side=tk.LEFT, padx=5)

        tk.Label(filter_frame, text="до:").pack(side=tk.LEFT, padx=5)
        self.filter_date_to = tk.Entry(filter_frame, width=12)
        self.filter_date_to.pack(side=tk.LEFT, padx=5)

        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.pack(side=tk.LEFT, padx=10)

        # Сумма за период
        self.sum_label = tk.Label(root, text="Сумма за период: 0.00", font=("Arial", 10, "bold"))
        self.sum_label.grid(row=3, column=0, columnspan=7, pady=10)

        self.refresh_table()

    def load_data(self):
        """Загружает данные из JSON-файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.expenses = []
        else:
            self.expenses = []

    def save_data(self):
        """Сохраняет данные в JSON-файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except PermissionError:
            messagebox.showerror("Ошибка", f"Нет прав на запись в файл:\n{DATA_FILE}\n\n"
                                         f"Попробуйте:\n"
                                         f"1. Закрыть файл expenses.json, если он открыт в другой программе\n"
                                         f"2. Запустить программу от имени администратора\n"
                                         f"3. Переместить программу в другую папку (например, на рабочий стол)")

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_entry.get().strip()

        if not amount_str or not category or not date_str:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return

        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        self.expenses.append({"date": date_str, "category": category, "amount": amount})
        self.save_data()
        self.refresh_table()
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def apply_filter(self):
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = self.expenses[:]
        cat_filter = self.filter_category.get()
        if cat_filter != "Все":
            filtered = [e for e in filtered if e["category"] == cat_filter]

        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()

        if date_from:
            if not self.validate_date(date_from):
                messagebox.showerror("Ошибка", "Неверный формат 'Дата от'")
                return
            filtered = [e for e in filtered if e["date"] >= date_from]

        if date_to:
            if not self.validate_date(date_to):
                messagebox.showerror("Ошибка", "Неверный формат 'Дата до'")
                return
            filtered = [e for e in filtered if e["date"] <= date_to]

        for exp in filtered:
            self.tree.insert("", tk.END, values=(exp["date"], exp["category"], f"{exp['amount']:.2f}"))

        total = sum(e["amount"] for e in filtered)
        self.sum_label.config(text=f"Сумма за период: {total:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
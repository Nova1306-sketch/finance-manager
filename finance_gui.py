# finance_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from finance_classes import Transaction, FinanceManager, TransactionType


class FinanceApp:
    """Графический интерфейс для работы с личными финансами."""

    def __init__(self, root: tk.Tk):
        self.manager = FinanceManager()
        self.root = root
        self.root.title("Учет личных финансов")
        self.root.geometry("800x600")
        self.setup_ui()

    def setup_ui(self) -> None:
        """Создаёт все элементы интерфейса."""

        # ----- Фрейм для ввода данных -----
        input_frame = ttk.LabelFrame(self.root, text="Добавить операцию", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поле "Сумма"
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky=tk.W)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=2)

        # Поле "Категория"
        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, state="readonly")
        categories = [cat.name for cat in self.manager.categories]
        self.category_combo["values"] = categories
        if categories:
            self.category_combo.current(0)
        self.category_combo.grid(row=1, column=1, padx=5, pady=2)

        # Поле "Дата"
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, padx=5, pady=2)

        # Поле "Описание"
        ttk.Label(input_frame, text="Описание:").grid(row=3, column=0, sticky=tk.W)
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=3, column=1, padx=5, pady=2)

        # ----- Кнопки -----
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame,
            text="Добавить операцию",
            command=self.add_transaction
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Удалить выбранную",
            command=self.delete_transaction
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Аналитика",
            command=self.show_analytics
        ).pack(side=tk.LEFT, padx=5)

        # ----- Информация о балансе -----
        info_frame = ttk.LabelFrame(self.root, text="Финансовая информация", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.balance_label = ttk.Label(info_frame, text="", font=("Arial", 12, "bold"))
        self.balance_label.pack()
        self.update_balance()

        # ----- Таблица операций -----
        table_frame = ttk.LabelFrame(self.root, text="История операций", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("#1", "#2", "#3", "#4", "#5")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("#1", text="Дата")
        self.tree.heading("#2", text="Категория")
        self.tree.heading("#3", text="Тип")
        self.tree.heading("#4", text="Сумма")
        self.tree.heading("#5", text="Описание")

        self.tree.column("#1", width=100)
        self.tree.column("#2", width=120)
        self.tree.column("#3", width=80)
        self.tree.column("#4", width=100)
        self.tree.column("#5", width=200)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.update_table()

    # ---------- Логика кнопок ----------

    def add_transaction(self) -> None:
        """Обработка добавления новой операции из полей ввода."""
        try:
            amount_text = self.amount_entry.get().strip()
            category_name = self.category_var.get().strip()
            date_text = self.date_entry.get().strip()
            description = self.desc_entry.get().strip()

            if not amount_text or not category_name or not date_text:
                messagebox.showwarning("Ошибка", "Заполните обязательные поля!")
                return

            amount = float(amount_text)

            # Простая проверка формата даты
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
                return

            category = next(
                (cat for cat in self.manager.categories if cat.name == category_name),
                None,
            )
            if not category:
                messagebox.showwarning("Ошибка", "Выберите корректную категорию!")
                return

            transaction = Transaction(amount, category, date_text, description)
            self.manager.add_transaction(transaction)

            self.update_table()
            self.update_balance()
            self.clear_inputs()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму (число)!")

    def delete_transaction(self) -> None:
        """Удаляет выбранную строку из таблицы и менеджера."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Удаление", "Выберите запись для удаления.")
            return

        index = self.tree.index(selected[0])

        self.manager.delete_transaction(index)
        self.update_table()
        self.update_balance()

    def show_analytics(self) -> None:
        """Открывает отдельное окно с суммами по категориям."""
        summary = self.manager.get_category_summary()
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Аналитика по категориям")
        analytics_window.geometry("300x400")

        if not summary:
            ttk.Label(analytics_window, text="Нет данных для анализа.").pack(padx=10, pady=10)
            return

        for category, amount in summary.items():
            # Доход — плюс, расход — минус
            text = f"{category}: {amount:.2f} руб."
            label = ttk.Label(analytics_window, text=text)
            label.pack(padx=10, pady=2, anchor=tk.W)

    # ---------- Вспомогательные методы ----------

    def update_table(self) -> None:
        """Перерисовывает таблицу операций."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for transaction in self.manager.transactions:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    transaction.date,
                    transaction.category.name,
                    transaction.category.type.value,
                    f"{transaction.amount:.2f}",
                    transaction.description,
                ),
            )

    def update_balance(self) -> None:
        """Обновляет отображение текущего баланса."""
        balance = self.manager.get_balance()
        color = "green" if balance >= 0 else "red"
        self.balance_label.config(
            text=f"Текущий баланс: {balance:.2f} руб.",
            foreground=color,
        )

    def clear_inputs(self) -> None:
        """Очищает поля ввода после добавления операции."""
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()

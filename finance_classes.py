# finance_classes.py
import csv
from enum import Enum


class TransactionType(Enum):
    """Тип финансовой операции: доход или расход."""
    INCOME = "Доход"
    EXPENSE = "Расход"


class Category:
    """Категория операции (имя + тип)."""

    def __init__(self, name: str, type: TransactionType):
        self.name = name
        self.type = type

    def __repr__(self) -> str:
        return f"Category(name={self.name!r}, type={self.type.value!r})"


class Transaction:
    """Финансовая операция."""

    def __init__(self, amount: float, category: Category, date: str, description: str = ""):
        """
        :param amount: сумма операции (положительное число)
        :param category: объект Category
        :param date: строка с датой (формат 'ГГГГ-ММ-ДД')
        :param description: комментарий
        """
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

    def __repr__(self) -> str:
        return (f"Transaction(amount={self.amount}, category={self.category.name!r}, "
                f"date={self.date!r}, description={self.description!r})")


class FinanceManager:
    """
    Управляет списком операций:
    - хранит категории;
    - добавляет/удаляет операции;
    - считает баланс и аналитику;
    - сохраняет/загружает CSV.
    """

    def __init__(self, filename: str = "transactions.csv"):
        self.filename = filename
        self.transactions: list[Transaction] = []

        # Предустановленные категории
        self.categories: list[Category] = [
            Category("Зарплата", TransactionType.INCOME),
            Category("Инвестиции", TransactionType.INCOME),
            Category("Продукты", TransactionType.EXPENSE),
            Category("Транспорт", TransactionType.EXPENSE),
            Category("Развлечения", TransactionType.EXPENSE),
        ]

        # При запуске пробуем загрузить ранее сохранённые операции
        self.load_from_file()

    def add_transaction(self, transaction: Transaction) -> None:
        """Добавить операцию и сразу сохранить в файл."""
        self.transactions.append(transaction)
        self.save_to_file()

    def delete_transaction(self, index: int) -> None:
        """Удалить операцию по индексу и пересохранить файл."""
        if 0 <= index < len(self.transactions):
            del self.transactions[index]
            self.save_to_file()

    def get_balance(self) -> float:
        """Вернуть текущий баланс (доходы - расходы)."""
        income = sum(
            t.amount for t in self.transactions
            if t.category.type == TransactionType.INCOME
        )
        expenses = sum(
            t.amount for t in self.transactions
            if t.category.type == TransactionType.EXPENSE
        )
        return income - expenses

    def get_category_summary(self) -> dict:
        """
        Вернуть словарь вида:
        { 'Продукты': -5000, 'Зарплата': 30000, ... }
        """
        summary: dict[str, float] = {}
        for transaction in self.transactions:
            cat_name = transaction.category.name
            if cat_name not in summary:
                summary[cat_name] = 0.0

            if transaction.category.type == TransactionType.INCOME:
                summary[cat_name] += transaction.amount
            else:
                summary[cat_name] -= transaction.amount
        return summary

    def save_to_file(self) -> None:
        """Сохранить все операции в CSV."""
        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Amount", "Category", "Type", "Date", "Description"])
            for transaction in self.transactions:
                writer.writerow([
                    transaction.amount,
                    transaction.category.name,
                    transaction.category.type.value,
                    transaction.date,
                    transaction.description,
                ])

    def load_from_file(self) -> None:
        """Загрузить операции из CSV, если файл существует."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Находим категорию по имени
                    category = next(
                        (cat for cat in self.categories if cat.name == row["Category"]),
                        None,
                    )
                    # Если категория есть в списке — создаём операцию
                    if category:
                        transaction = Transaction(
                            amount=float(row["Amount"]),
                            category=category,
                            date=row["Date"],
                            description=row.get("Description", ""),
                        )
                        self.transactions.append(transaction)
        except FileNotFoundError:
            # Если файла нет — просто начинаем с пустого списка операций
            self.transactions = []

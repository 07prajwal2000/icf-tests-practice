# balance, account_id, outgoing, incoming, transactions(type: debit|credit, amount, sent_to, timestamp)

from typing import Literal

type TransactionType = Literal["debit", "credit", "withdraw", "cashback"]
type TransactionStatus = Literal["completed", "pending", "cashback_received"]


class Transaction:
    def __init__(
        self,
        id: str,
        amount: int,
        type: TransactionType,
        owner: str,
        target: str,
        balance_after_tx: int,
        created_at: int,
        status: TransactionStatus = "completed",
    ):
        self.id = id
        self.amount = amount
        self.type = type
        self.owner = owner
        self.target = target
        self.balance_after_transaction = balance_after_tx
        self.created_at = created_at
        self.status = status


class Cashback:
    def __init__(self, amount: int, available_on: int, payment_id: str):
        self.amount = amount
        self.available_on = available_on
        self.payment_id = payment_id
        self.status: TransactionStatus = "pending"


class Account:
    def __init__(self, balance: int, account_id: str, created_on: int):
        self.balance = balance
        self.account_id = account_id
        self.total_incoming = 0
        self.total_outgoing = 0
        self.account_creation_ts = created_on
        self.transactions: list[Transaction] = []
        self.pending_cashbacks: list[Cashback] = []

    def __str__(self):
        return f"Account(balance={self.balance}, account_id={self.account_id}, total_incoming={self.total_incoming}, total_outgoing={self.total_outgoing})"

    def get_balance(self):
        return self.balance

    def credit_amount(
        self,
        ts: int,
        amount: int,
        from_account: str = "",
        type: TransactionType = "credit",
    ):
        if from_account.strip(" ") == "":
            from_account = self.account_id

        self.balance += amount
        self.total_incoming += amount

        new_transaction = Transaction(
            id=f"{self.account_id}-{ts}",
            amount=amount,
            type="credit",
            balance_after_tx=self.get_balance(),
            owner=self.account_id,
            target=from_account,
            created_at=ts,
        )
        self.transactions.append(new_transaction)

    def debit_amount(self, ts: int, amount: int, target_account: str = "") -> bool:
        if self.balance < amount:
            return False

        self.balance -= amount
        self.total_outgoing += amount

        is_current_user = (
            target_account == self.account_id or target_account.strip() == ""
        )

        tx_type: TransactionType = "withdraw" if is_current_user else "debit"
        new_transaction = Transaction(
            id=f"{self.account_id}-{ts}",
            amount=amount,
            type=tx_type,
            balance_after_tx=self.get_balance(),
            owner=self.account_id,
            target=target_account,
            created_at=ts,
        )
        self.transactions.append(new_transaction)
        return True

    def transfer(self, ts: int, target_account: "Account", amount: int) -> bool:
        success = self.debit_amount(
            ts=ts, amount=amount, target_account=target_account.account_id
        )
        if not success:
            return False
        target_account.credit_amount(ts=ts, amount=amount, from_account=self.account_id)
        return True

    def pay(self, ts: int, amount: int) -> str | None:
        success = self.debit_amount(ts=ts, amount=amount, target_account="merchant")
        if not success:
            return False
        cashback_amount = round(float(amount) * 0.02)
        cashback_available = (1000 * 60 * 60 * 24) + ts
        cashback_to_apply = Cashback(
            amount=cashback_amount,
            available_on=cashback_available,
            payment_id=f"payment-{ts}",
        )
        self.pending_cashbacks.append(cashback_to_apply)

    def check_payment(self, ts: int, payment_id: str) -> None | str:
        selected = None
        for cashback in self.pending_cashbacks:
            if payment_id == cashback.payment_id:
                selected = cashback
                break
        if selected == None:
            return None
        if ts >= selected.available_on and selected.status == "pending":
            self.credit_amount(
                ts=ts, amount=selected.amount, from_account="merchant", type="cashback"
            )
            selected.status = "cashback_received"
        return selected.status

    def apply_pending_cashback(self, ts: int):
        for cashback in self.pending_cashbacks:
            self.check_payment(ts=ts, payment_id=cashback.payment_id)

from src.account import Account


class Bank:
    accounts: dict[str, Account]

    def __init__(self):
        self.accounts = {}

    def create_account(self, timestamp: int, account_id: str) -> bool:
        if account_id in self.accounts:
            return False
        new_account = Account(0, account_id, timestamp)
        self.accounts[account_id] = new_account
        self.on_tick(timestamp)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        account.credit_amount(ts=timestamp, amount=amount)
        self.on_tick(timestamp)
        return account.get_balance()

    def transfer(
        self,
        timestamp: int,
        source_account_id: str,
        target_account_id: str,
        amount: int,
    ) -> int | None:
        if source_account_id == target_account_id:
            return None
        if (
            source_account_id not in self.accounts
            or target_account_id not in self.accounts
        ):
            return None
        source_account = self.accounts[source_account_id]
        target_account = self.accounts[target_account_id]
        success = source_account.transfer(
            ts=timestamp, target_account=target_account, amount=amount
        )
        if not success:
            return None
        self.on_tick(timestamp)
        return source_account.get_balance()

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        sorted_accounts = sorted(
            self.accounts.values(),
            key=lambda account: (account.total_outgoing, account.account_id),
            reverse=True,
        )
        self.on_tick(timestamp)
        result: list[str] = []
        for account in sorted_accounts[:n]:
            result.append(f"{account.account_id}({account.total_outgoing})")
        return result

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        success = account.pay(ts=timestamp, amount=amount)
        if not success:
            return None
        self.on_tick(timestamp)
        return success

    def on_tick(self, timestamp: int):
        for account in self.accounts.values():
            account.apply_pending_cashback(timestamp)

    def merge_accounts(
        self, timestamp: int, target_account_id: str, source_account_id: str
    ) -> bool:
        if source_account_id == target_account_id:
            return False
        if (
            source_account_id not in self.accounts
            or target_account_id not in self.accounts
        ):
            return False
        source_account = self.accounts[source_account_id]
        target_account = self.accounts[target_account_id]

        # Merge balances and transactions
        target_account.balance += source_account.balance
        target_account.total_incoming += source_account.total_incoming
        target_account.total_outgoing += source_account.total_outgoing
        target_account.transactions.extend(source_account.transactions)
        target_account.pending_cashbacks.extend(source_account.pending_cashbacks)

        # Remove the source account
        del self.accounts[source_account_id]
        self.on_tick(timestamp)
        return True

    def get_balance(self, timestamp: int, account_id: str) -> int | None:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        self.on_tick(timestamp)
        return account.get_balance()

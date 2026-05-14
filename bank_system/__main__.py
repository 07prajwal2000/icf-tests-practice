from src.bank import Bank

bank = Bank()
bank.create_account(1, "acc-1")
bank.create_account(2, "acc-2")
bank.create_account(3, "acc-3")
bank.deposit(4, "acc-3", 2000)
bank.deposit(5, "acc-2", 3000)
bank.deposit(6, "acc-3", 4000)
print(", ".join(bank.top_spenders(7, 3)))
bank.transfer(8, "acc-3", "acc-2", 500)
bank.transfer(9, "acc-3", "acc-1", 1000)
bank.deposit(10, "acc-1", 3000)
bank.transfer(12, "acc-1", "acc-2", 2500)
print(", ".join(bank.top_spenders(13, 3)))
bank.pay(14, "acc-1", 100)
print(", ".join(bank.top_spenders(15, 3)))
bank.pay(16, "acc-2", 300)
next_day_ts = 1000 * 60 * 60 * 24
print(", ".join(bank.top_spenders(100 + next_day_ts, 3)))
print(bank.deposit(100 + next_day_ts, "acc-3", 500))

print("merged", bank.merge_accounts(200 + next_day_ts, "acc-1", "acc-2"))
print(bank.get_balance(300 + next_day_ts, "acc-1"))

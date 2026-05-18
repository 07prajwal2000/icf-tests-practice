from workers.src.system import WorkerSystem

if __name__ == "__main__":
    system = WorkerSystem()
    print(system.add_worker("john", "junior dev", 120))
    print(system.add_worker("jason", "junior dev", 150))
    print(system.add_worker("ashley", "junior dev", 150))
    print(system.register("john", 100))
    print(system.register("john", 150))
    print(system.register("jason", 200))
    print(system.register("jason", 250))
    print(system.register("jason", 275))
    print(system.top_n_workers(5, "junior dev"))
    print(system.top_n_workers(1, "junior dev"))
    print(system.register("ashley", 400))
    print(system.register("ashley", 500))
    print(system.register("jason", 575))
    print(system.top_n_workers(3, "junior dev"))
    print(system.top_n_workers(3, "mid dev"))

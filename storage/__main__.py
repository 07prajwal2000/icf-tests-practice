from filesystem import FileSystem

if __name__ == "__main__":
    fs = FileSystem()
    print("LEVEL 1")
    print(fs.file_upload("name.txt", 10))
    print(fs.file_upload("file.txt", 12))
    try:
        print(fs.file_upload("file.txt", 50))
    except Exception as e:
        print("Error", e)
    print(fs.file_get("file.txt"))
    print(fs.file_get("file-a.txt"))
    print(fs.file_copy("file.txt", "file-x.txt"))
    print(fs.file_get("file-x.txt"))
    print("\nLEVEL 2")
    print(fs.file_search("file"))
    print(fs.file_search("non-existing"))
    print("\nLEVEL 3")
    print(fs.file_upload_at(timestamp=1, file_name="x.txt", file_size=100))
    print(
        fs.file_upload_at(timestamp=2, file_name="y.txt", file_size=110, ttl=5)
    )  # expires at 6
    print(fs.file_get_at(timestamp=3, file_name="x.txt"))
    print(fs.file_get_at(timestamp=4, file_name="y.txt"))
    print(fs.file_copy_at(timestamp=5, file_from="x.txt", file_to="z.txt"))
    print(fs.file_get_at(timestamp=6, file_name="y.txt"))  # before expiry
    print(fs.file_get_at(timestamp=7, file_name="y.txt"))  # after expiry
    print(fs.file_search_at(timestamp=8, prefix="x"))

    print("\nLEVEL 4")
    print(fs.file_upload_at(timestamp=10, file_name="a.txt", file_size=100))
    print(fs.file_upload_at(timestamp=11, file_name="b.txt", file_size=110))
    print(fs.file_upload_at(timestamp=12, file_name="c.txt", file_size=120))
    print(fs.file_get_at(timestamp=13, file_name="a.txt"))
    print(fs.rollback(timestamp=11))
    print(fs.file_get_at(timestamp=14, file_name="b.txt"))
    print(fs.file_get_at(timestamp=15, file_name="c.txt"))

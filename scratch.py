def main():
    main_list = ["Hi", "Howdy"]
    manipulate_list(main_list)
    print(main_list)

def manipulate_list(test_list):
    test_list.append("Hello")

if __name__ == "__main__":
    main()
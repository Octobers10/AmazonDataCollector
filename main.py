import basic_main
import review_main
import search_main

def main():
    print("====================================================================")
    print("        Welcome to use Amazon Data Collection Tool 1.0        ")
    print("====================================================================")
    print("Instruction: ")
    while (True):
        print("Select the data you want to collect:")
        print("1. Collect product rankings by keywords")
        print("2. Collect product basic info by ASIN")
        print("3. Collect product review info by ASIN")
        print("4. Quit")
        file_option=input()
        
        if file_option == '1':
            search_main.main()
        elif file_option == '2':
            basic_main.main()
        elif file_option == '3':
            review_main.main()
        elif file_option == '4':
            break
        else:
            print("Invalid option. Please enter 1, 2, 3, or 4 (no space and comma)")
            continue
    print("Thank you for using Amazon Data Collection Tool 1.0!")
    

            
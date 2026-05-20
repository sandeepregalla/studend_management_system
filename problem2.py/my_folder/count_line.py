# import sys

# def count_lines(filename):
#     with open(filename)as f:
#         return len(f.readlines())
    

# if __name__=="__main__":
#     filename = sys.argv[1]
#     num_lines = count_lines(filename)
#     print(f"there are {num_lines} lines in {filename}")

import sys 

def count_lines(filename):
    with open(filename)as f:
        return len(f.readlines())
    
if __name__ == "__main__":
    filename = sys.argv[1]
    num_lines = count_lines(filename)
    print(f"there are {num_lines} lines in {filename}")    
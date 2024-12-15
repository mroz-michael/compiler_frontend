import os
from parser import Parser
from scanner import Lexer

def main():
    print("Welcome! Please check the readme for details about the language/grammar and input requirements")
    file_name = input("Please enter the name of the file you'd like to tokenize:")
    if os.path.isfile(file_name):
        with open(file_name, 'r') as file:
            input_file = file.read()
            lexer = Lexer(input_file)
            tokens = lexer.tokenize()
        with open(f"{file_name}_token_stream", "w") as output_file:
            print(f"Printing token stream to: {file_name}_token_stream")
            for token in tokens:
                print(token)
                output_file.write(str(token))
                if not token.type == "EOF":
                    output_file.write("\n")
        print("Token stream printed. Initializing Parser")
        with open(f"{file_name}_token_stream", 'r') as parse_file:
            token_stream = parse_file.read()
            parser = Parser(token_stream)
            outputs = parser.parse() #returns [parse tree, error_report]
            
            with open(f"{file_name}_parse_tree", "w") as output_file:
                print(f"Printing parse tree for {file_name}")
                for token in outputs[0]:
                    print(token)
                    output_file.write(token + "\n")
                if len(outputs[1]) > 0:
                    print("\n")
                    for error in outputs[1]:
                        print(error)
                        output_file.write(error + "\n")
    else:
        print(f"File: {file_name} not found. Please recheck the name or file path")
        
if __name__ == "__main__":
    main()
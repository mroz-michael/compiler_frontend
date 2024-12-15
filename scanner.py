import os

class TokenType:
    LBRACE = "LBRACE", # {
    RBRACE = "RBRACE", # }   
    LBRACK = "LBRACK", # [
    RBRACK = "RBRACK", # ]
    COLON = "COLON", # :
    COMMA = "COMMA", # ,
    INTEGER = 'INTEGER',
    FLOAT = 'FLOAT',
    STRING = 'STRING', #
    TRUE = "TRUE", 
    FALSE = "FALSE",
    NULL = "NULL",
    EOF = "EOF"  # end of input
    
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        
    def __repr__(self):
        if self.type == TokenType.LBRACE:
            return "<{>"
        if self.type == TokenType.RBRACE:
            return  "<}>"
        if self.type == TokenType.LBRACK:
            return "<[>"
        if self.type == TokenType.RBRACK:
            return "<]>"
        if self.type == TokenType.COLON:
            return "<:>"
        if self.type == TokenType.COMMA:
            return "<,>"
        if self.type == TokenType.INTEGER or self.type == TokenType.FLOAT:
            return f"<number, {self.value}>" 
        # if self.type == TokenType.FLOAT:
        #     return f"<Float, {self.value}>"
        if self.type == TokenType.STRING:
            return f"<string, {self.value}>"
        if self.type == TokenType.FALSE:
            return f"<false>"
        if self.type == TokenType.TRUE:
            return "<true>"
        if self.type == TokenType.NULL:
            return f"<null>"
        #only other option currently is eof
        return f"<{self.type}>"

class DFA:
    def __init__(self):
        #state labels stored in array for reference, please see written report for detailed explanation of DFA
        self.states = [
            "start",
            "str0", #start of string path
            "num0", #start of number path
            "dec", #state after reading a decimal
            "flt", #number with decimal . (float)
            "m", #negative sign
            "z", #leading zero
            "t0", #the t of True
            "t1", #the r in True
            "t2", #the u in True
            "f0", #the f in False
            "f1", #the a in False
            "f2", #the l in False
            "f3", #the s in False
            "n0", #the n in null
            "n1", #the u in null
            "n2", #the 1st l in null
            "reject" #dead state
        ]
        self.state = self.states[0]
        
    def transition(self, char, next, token_value):    
        if self.state == "start":
            '''
            In start state, the following can happen:
            We read a valid single-character symbol -> accept input create token
            We read T, F, or N -> go to start of True/False/Null paths, respectively
            We read a " -> go to start of string path
            We read a minus sign -> go to intermediary state before number path
            We read a 0 -> go to intermediary state before number path
            We read a [1-9] -> go to start of number path
            We read an invalid single-character symbol -> reject input, handle error. 
            '''
            if char in ["{", "}", "[", "]", ":", ","]: #using nested if blocks to keep track of things
                if char == "{":
                    return Token(TokenType.LBRACE)
                if char == "}":
                    return Token(TokenType.RBRACE)
                if char == "[":
                    return Token(TokenType.LBRACK)
                if char == "]":
                    return Token(TokenType.RBRACK)
                if char == ":":
                    return Token(TokenType.COLON)
                if char == ",":
                    return Token(TokenType.COMMA)
            if char in ["t", "f", "n"]: # begin true|false|null path
                if char == "t":
                    self.state = "t0"
                    return
                if char == "f":
                    self.state = "f0"
                    return
                if char == "n":
                    self.state = "n0"
                    return
            if char == '"': #start of string path
                token_value += char
                self.state = "str0"
                return
            if char == "-": #intermediary state before number path
                token_value += char
                self.state = "m"
                return
            if char == "0":
                #if next char is a valid token start, create 0 as its own token and stay in start state
                if next is not None and next in ["{", "}", "[", "]", ":", ",", "t", "f", "n", '"'] or next.isspace():
                    return Token(TokenType.INTEGER, 0)
                
                #else go to intermediary state to see if a decimal follows the 0
                token_value += char
                self.state = "z"
                return
            if char.isnumeric(): #number starts from 1 to 9
                token_value += char
                #if next char is a valid token start, tokenize this single digit and stay in start
                if next is not None and next in ["{", "}", "[", "]", ":", ",", "t", "f", "n", '"'] or next.isspace():
                    return Token(TokenType.INTEGER, token_value)
                #else, go to start of number path
                self.state = "num0"
                return
            self.state = "reject"
            return
        
        #string state
        if self.state == "str0": 
            token_value += char
            if char != '"':
                return
            if char == '"':
                self.state = "start"
                return Token(TokenType.STRING, token_value)
            
        #states for reaing boolean: true
        if self.state == "t0":   
            if char == "r":
                self.state = "t1"
                return
            self.state = "reject"
            return 
        
        if self.state == "t1":
            if char == "u":
                self.state = "t2"
                return
            
            self.state = "reject"
            return
        
        if self.state == "t2":
            if char == "e":
                self.state = "start"
                return Token(TokenType.TRUE)
            
            self.state = "reject"
            return
            
        #states for reading boolean: false    
        if self.state == "f0": 
            if char == "a":
                self.state = "f1"
                return
            
            self.state = "reject"
            return
        
        if self.state == "f1":
            if char == "l":
                self.state = "f2"
                return
            
            self.state = "reject"
            return
        
        if self.state == "f2":
            if char == "s":
                self.state = "f3"
                return
            
            self.state = "reject"
            return
        
        if self.state == "f3":
            if char == "e":
                self.state = "start"
                return Token(TokenType.FALSE)
            
            self.state = "reject"
            return
        
        #states for reading null    
        if self.state == "n0":    
            if char == "u":
                self.state = "n1"
                return
            
            self.state = "reject"
            return
        
        if self.state == "n1":
            if char == "l":
                self.state = "n2"
                return
            
            self.state = "reject"
            return
        
        if self.state == "n2":
            if char == "l":
                self.state = "start"
                return Token(TokenType.NULL)
            
            self.state = "reject"
            return
            
        if self.state == "m": ##if a minus sign was read from start state, next valid char must be digit
            #if current char is digit and next char is start of valid token, create token of -char and change state
            if char.isnumeric():
                if next is not None:
                    if next in ["{", "}", "[", "]", ":", ",", "t", "f", "n", '"'] or next.isspace():
                        self.state = "start"
                        token_value += char
                        return Token(TokenType.INTEGER, token_value)
                    
            if char == "0": #if -0, send to intermediary state to handle leading zeroes 
                token_value += char
                self.state = "z"
                return
            
            if char.isnumeric():
                token_value += char
                self.state = "num0"
                return
            
            self.state = "reject"
            return
        
        if self.state == "z": #if leading 0, it must be single digit or followed by decimal
            if char.isspace():
                self.state = "start"
                return Token(TokenType.INTEGER, token_value)
            if char == ".":
                token_value += char
                self.state = "dec" 
                return
            
            self.state = "reject"
            return
            
        if self.state == "dec": #decimal must be followed by a digit
            if char.isnumeric():
                token_value += char
                self.state = "flt" #path for numbers with a decimal
                return
            
            self.state = "reject"
            return
        
        if self.state == "flt": #number with decimal cannot have another
            if char.isnumeric():
                token_value += char
                #if next char is not none, check if its the start of a new valid token
                if (next is not None):
                    if next in ["{", "}", "[", "]", ":", ",", "t", "f", "n", '"'] or char.isspace():
                        self.state = "start"
                        return Token(TokenType.FLOAT, token_value)
            
                #else stay in flt state
                return
            if char.isspace(): #if space, tokenize and dont add space to token's value
                self.state = "start"
                return Token(TokenType.FLOAT, token_value)
            
            self.state = "reject"
            return
        
        if self.state == "num0": #dfa path for integers
            if char == ".":
                token_value += char
                self.state = "dec" #send to dec to check for possible float path
                return
            if char.isnumeric():
                token_value += char
                #if next char is a valid start of token, tokenize the number and change state
                if next is not None:
                    if next in ["{", "}", "[", "]", ":", ",", "t", "f", "n", '"'] or char.isspace():
                        self.state = "start"
                        return Token(TokenType.INTEGER, token_value)
                    
                #else stay in num0
                return
            
            if char.isspace(): #if space, tokenize number without adding the space
                self.state = "start"
                return Token(TokenType.INTEGER, token_value)
            
            self.state = "reject"
            return
        
class LexerError(Exception):
    def __init__(self, pos, char):
        if char is not None and char != " ":
            super().__init__(f"Invalid character '{char}' at index {pos} of input")
        elif char is not None:
            super().__init__(f"Unexpected whitespace at index {pos} of input")
        elif char is None:
            super().__init__(f"Unexpected end of input.")

class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0
        self.current_char = self.input_text[self.position] if self.input_text else None
        #create forward pointer
        self.next_char = self.input_text[self.position + 1] if len(self.input_text) > 1 else None
        self.dfa = DFA()
        
    def advance(self):
        self.position += 1
        if self.position >= len(self.input_text):
            self.current_char = None
            self.next_char = None
        elif self.position + 1 < len(self.input_text):
            self.current_char = self.input_text[self.position]
            self.next_char = self.input_text[self.position + 1]
        else: #if at last char, set forward pointer to None
            self.current_char = self.input_text[self.position]
            self.next_char = None
            
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
            
    def get_next_token(self):
        token_value = ""
        while self.current_char is not None:
            curr_value = self.current_char
            if self.current_char.isspace() and len(token_value) == 0: #dont skip whitespace if token is in progress
                self.skip_whitespace()
                continue
            
            token = self.dfa.transition(self.current_char, self.next_char, token_value) #final states return Token objects
            if self.dfa.state == "reject":
                raise LexerError(self.position, self.current_char)
            
            self.advance()
            token_value += curr_value            
            
            #if state is final, return token 
            if token is not None:
                return token
        
        #if last character in file was a number, return the number as a token before returning EOF token
        if token_value.isnumeric():
            return Token(TokenType.INTEGER, token_value)
        
        #check for negative integer in progress: 
        elif ( len(token_value) > 1 and token_value[0] == "m" and token_value[1:].isnumeric() ):
            return Token(TokenType.INTEGER, token_value)
        
        #check for float in progress:
        elif "." in token_value and token_value.replace(".", "").isnumeric():
            return Token(TokenType.FLOAT, token_value)
        
        #check if non-finalized token in progress:
        elif len(token_value) > 0:
            raise LexerError(self.position, self.current_char)
    
        return Token(TokenType.EOF)
       
    def tokenize(self):
        tokens = []
        while True:
            try:
                token = self.get_next_token()
            except LexerError as e:
                print(f"Lexical Error: {e}")
                break
            
            tokens.append(token)
            
            if token.type == TokenType.EOF:
                break
            
        return tokens

def main():
    print("Welcome! Please check the readme for details about the language/grammar and input requirements")
    file_name = input("Please enter the name of the file you'd like to tokenize:")
    if os.path.isfile(file_name):
        with open(file_name, 'r') as file:
            input_file = file.read()
            lexer = Lexer(input_file)
            tokens = lexer.tokenize()
        with open(f"result_{file_name}.txt", "w") as output_file:
            print(f"Printing token stream to: result_{file_name}")
            for token in tokens:
                print(token)
                output_file.write(str(token))
                if not token.type == "EOF":
                    output_file.write("\n")
    else:
        print(f"File: {file_name} not found. Please recheck the name or file path")
        
if __name__ == "__main__":
    main()
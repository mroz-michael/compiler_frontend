class Token:
    def __init__(self, token_string):
        self.token_type = self.get_token_type(token_string)
        self.token_value = self.get_token_value(token_string)
    
    def __repr__(self):
        return self.token_type + " " + self.token_value if self.token_value else self.token_type
        
    def get_token_value(self, token):
        #extract the value of Number or String tokens, other tokens have no value attribute
        if token[1:7] == "string" or token[1:7] == "number":
            return token[8:-1].strip()
        return None
        
    #determine type of token based on its string representation
    def get_token_type(self, token):
        if token == "<{>":
            return "{"
        if token == "<}>":
            return "}"
        if token == "<[>":
            return "["
        if token == "<]>":
            return "]"
        if token == "<:>":
            return ":"
        if token == "<,>":
            return ","
        if token[1:7].lower() == "number":
            return "NUMBER"
        if token == "<true>":
            return "true"
        if token == "<false>":
            return "false"
        if token == "<null>":
            return "null"
        if token[1:7].lower() == "string":
            return "STRING"
        if token == "<EOF>":
            return "EOF"

class Parser:
    def __init__(self, token_stream):
        self.token_pointer = -1 #first call to get_next_token will set pointer to start of token stream 
        self.lookahead = 0 #point to token after current
        self.current_token = None
        self.next_token = None
        self.token_stream = token_stream.split('\n')
        self.tokens_eaten = [] #stores consumed tokens to be outputted as a parse tree
        self.error_list = [] #gather and report errors to user after giving parse tree
        self.tokens_discarded = [] #list of tokens removed during error recovery
        self.parse_tree = [] #list containing parse tree representation to output
        #convert the string tokens into Token objects
        for i in range(len(self.token_stream)):
            #remove trailing whitespaces if any between token inputs and instantiate Token objects 
            self.token_stream[i] = Token(self.token_stream[i].strip())
        #use this stack to determine which dict/list closing tokens are needed for error recovery
        self.recovery_stack = []
        self.is_recovered = False #true after error recovery, tells parser to resume parsing from a safe point
        self.is_finished = False #set to true after creating parse tree, tells parser to stop calling parse methods
        
    def get_next_token(self):
        self.token_pointer += 1
        self.lookahead += 1
        if self.token_pointer >= len(self.token_stream):
            self.current_token = None
            return
        if self.lookahead >= len(self.token_stream):
            self.next_token = None
        else:
            self.next_token = self.token_stream[self.lookahead]
        self.current_token = self.token_stream[self.token_pointer]
    
    #give parse tree representation of the non-terminals and terminals from parsed token stream
    def output(self):
        indentation = 0
        indentation_stack = [] #when we see a { or [, push the current indentation level to the stack
                                #when we see a } or ], pop the current indentation level 
        '''
            Indentation pseudocode:
            if value | list | dict | pair -> increase indentation after printing
            if  , or : -> print without changing indentation
            if String/Number/true/false/null ->  print then reduce indentation
            for nested brackets and braces:
              everytime you see a { or [, save the indentation for it to a stack
              then when you see a } or ], pop from the stack to get the corresponding indentation
        '''
        for token in self.tokens_eaten:
            
            if token in ["value", "list", "dict", "pair"]:
                self.parse_tree.append(" " * indentation + token)
                indentation += 2
            elif token in ["{", "["]:
                self.parse_tree.append(" " * indentation + token)
                indentation_stack.append(indentation)
            elif token in [":", ","]:
                self.parse_tree.append( " " * indentation + token)
            
            elif token[0:6] == "STRING" or token[0:6] == "NUMBER" or token == "true" or token == "null" or token == "false":
                self.parse_tree.append(" " * indentation + token)
                indentation -= 2
            
            elif token in ["}","]"]:
                indentation = indentation_stack.pop()
                self.parse_tree.append(" " * indentation + token)
                indentation -= 2
        return self.parse_tree
              
    def parse(self):
        self.get_next_token()
        self.parse_value()
        
        if self.is_finished:
            return [self.parse_tree, self.error_list]
        
        return self.finish_parsing()
        
    def parse_value(self): # value --> dict | list | STRING | NUMBER | "true" | "false" | "null"
        
        if self.is_finished:
            return
        
        token_type = self.current_token.token_type
        #valid value can start with any of the following tokens: { [ string, number, true, false, null
        if token_type == "{":
            self.tokens_eaten.append("value")
            self.recovery_stack.append("}")
            self.parse_dict()
            return
        if token_type == "[":
            self.tokens_eaten.append("value")
            self.recovery_stack.append("]")
            self.parse_list()
            return
        #call eat on all other terminals
        if token_type in ["STRING", "NUMBER", "true", "false", "null"]:
            self.tokens_eaten.append("value")
            self.eat(self.current_token.token_type)
            return
        if token_type == "EOF":
            self.finish_parsing()
            self.is_finished = True
        else: #if unexpected token, enter error recovery mode
            if self.is_recovered or self.is_finished: #if just recovered from error, return
                self.is_recovered = False
                return
            self.panic_mode("value")
        
    def parse_dict(self): # dict --> ”{” pair (”, ” pair)∗ ”}”
        if self.is_finished:
            return
        self.tokens_eaten.append("dict")
        self.eat("{")
        self.parse_pair()
        #if recovered from a parsing error, finish the production rule
        if self.is_recovered or self.is_finished:
            self.is_recovered = False
            return
        #for kleene-*, comma denotes another pair
        while self.current_token.token_type == ",":
            self.eat(",")
            self.parse_pair()
        
        if self.is_recovered or self.is_finished:
            self.is_recovered = False
            return
        
        self.eat("}")
        
        
    def parse_list(self): #list --> ”[” value (”, ” value)∗ ”]”
        if self.is_finished or self.is_recovered:
            self.is_recovered = False
            return
        self.tokens_eaten.append("list")
        self.eat("[")
        self.parse_value()
        #for kleene-*, comma denotes another value
        while self.current_token.token_type == ",":
            self.eat(",")
            self.parse_value()
        
        if self.is_recovered or self.is_finished:
            self.is_recovered = False
            return        
        self.eat("]")
      
    def parse_pair(self): #pair : STRING ”:” value
        if self.is_finished or self.is_recovered:
            self.is_recovered = False
            return
        self.tokens_eaten.append("pair")
        self.eat("STRING")
        self.eat(":")
        self.parse_value()
    
    #consume token, add its string representation to tokens_eaten if valid else throw error
    def eat(self, expected_token):
        
        if self.is_finished:
            return
        
        if self.current_token.token_type == expected_token:
            to_print = self.current_token.token_type #token type and token value if exists
            
            #if current token is comma or colon, use lookahead to ensure next token is valid
            if self.current_token.token_type == "," or self.current_token.token_type == ":":
                if self.next_token and self.next_token.token_type not in ["{", "[", "STRING", "NUMBER", "true", "false", "null"]:
                    #if not a valid value, get rid of the comma or colon 
                    token = self.current_token.token_type
                    error_msg = f"unexpected token {self.next_token.token_type} after {token} at position {str(self.token_pointer)} -> discarding {token}."
                    self.error_list.append(error_msg)
                    self.is_recovered = True
                    self.get_next_token()
                    return
                    
            
            if self.current_token.token_value is not None:
                to_print += ": " + self.current_token.token_value
            self.tokens_eaten.append(to_print)
            
            #if closing innermost dict or list, pop most recent emergency closure from stack
            if self.current_token.token_type in ["]", "}"] and len(self.recovery_stack) > 0:
                self.recovery_stack.pop()
                
            if self.current_token.token_type != "EOF":
                self.get_next_token()
            
            if self.current_token.token_type == "EOF":
                self.finish_parsing()
                self.is_finished = True #if finished, set flag to true to avoid trying to parse more
            return
        
        self.panic_mode(expected_token)
        
    def panic_mode(self, expected):
        if self.is_finished: 
            return
        
        num_discarded = 1
        error_msg = "Parsing Error: Received token " + self.current_token.token_type
        error_msg += " expected token type: " + expected + " at position: " + str(self.token_pointer)
        self.error_list.append(error_msg)
    
        if self.current_token.token_type == "EOF": 
            self.finish_parsing()
            self.is_finished = True
       
        self.tokens_discarded.append(self.current_token)
        self.get_next_token()
        synchronizing_tokens = ["EOF"]
            #determine synchronizing token based on current parsing state
        if len(self.recovery_stack) > 0:
            if self.recovery_stack[-1] == "}":
                synchronizing_tokens.append("}")
            elif self.recovery_stack[-1] == "]":
                synchronizing_tokens.append("]")
        
        #get next token until curr token is synchronizing. Then resume parsing after that token (unless EOF)
        while not self.current_token.token_type in synchronizing_tokens:
            self.tokens_discarded.append(self.current_token)
            num_discarded += 1
            self.get_next_token()
        
        
        #since empty lists are not allowed in the grammar, check if the most recently
        #consumed token is [, if so insert an empty string to make the list syntactically valid
        if self.current_token.token_type == "]" and self.tokens_eaten[-1] == "[":
            error_msg = "Empty list detected, adding empty string"
            self.tokens_eaten.append("value")
            self.tokens_eaten.append('STRING: ""')
            self.error_list.append(error_msg)
        #same for empty dicts
        if self.current_token.token_type == "}" and self.tokens_eaten[-1] == "{":
            error_msg = "empty dict detected, adding empty pair"
            self.tokens_eaten.append("pair")
            self.tokens_eaten.append('STRING: ""')
            self.tokens_eaten.append(":")
            self.tokens_eaten.append('STRING: ""')
            self.error_list.append(error_msg)
        error_msg = f"Parsing resumed with token: {self.current_token} at position {str(self.token_pointer)}, tokens lost: {str(num_discarded)}"
        self.is_recovered = True #tells current parse_X function to stop the production rule
        self.error_list.append(error_msg)
        self.eat(self.current_token.token_type) #consume the recovery token
        
    #close unclosed lists/dicts, output parse tree, error report, and exit program
    def finish_parsing(self):
        self.is_finished = True #do not call any more production rules
        #if EOF was consumed, remove it so it doesnt end up in parse tree
        if self.tokens_eaten[-1] == "EOF":
            self.tokens_eaten.pop()
        
        #if any unclosed lists or dicts remain, close them starting with top of stack
        for closure in reversed(self.recovery_stack):
            closure_name = "list" if closure == "]" else "dict"
            #check if prev. appended token is the closure's opening, if so add an empty element to preserve grammar rule
            prev_token = self.tokens_eaten[-1]
            if prev_token == "[" and closure == "]":
                error_msg = "Empty list detected, adding empty string"
                self.tokens_eaten.append("value")
                self.tokens_eaten.append('STRING: ""')
                self.error_list.append(error_msg)
            if prev_token == "{" and closure == "}":
                error_msg = "empty dict detected, adding empty pair"
                self.tokens_eaten.append("pair")
                self.tokens_eaten.append('STRING: ""')
                self.tokens_eaten.append(":")
                self.tokens_eaten.append('STRING: ""')
                self.error_list.append(error_msg)
                
            self.tokens_eaten.append(closure)
            error_msg = "Fixing unclosed " + closure_name + " inserting " + closure
            self.error_list.append(error_msg)
            
        #handle case where grammar finished but additional tokens remain
        unread = len(self.token_stream) - len(self.tokens_eaten)
        if unread > 1 and not "EOF" in self.tokens_eaten: #1 to not count EOF as an unread token
            error_msg = f"Reached end of parsing with {unread} unparsed tokens remaining"
            self.error_list.append(error_msg)
            
        tree = self.output()
        error_report = []
        
        if len(self.error_list) > 0:
            error_report.append("Errors:\n")
            for error in self.error_list:
                error_report.append(error)
        return [tree, error_report]
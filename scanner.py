from token import Token, TokenType


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
        }

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def scan_token(self):
        c = self.advance()

        if c == ' ' or c == '\r' or c == '\t':
            return
        elif c == '\n':
            self.line += 1
            self.column = 1
            return
        elif c == '+':
            self.add_token(TokenType.PLUS, '+')
        elif c == '-':
            self.add_token(TokenType.MINUS, '-')
        elif c == '*':
            self.add_token(TokenType.MULTIPLY, '*')
        elif c == '/':
            if self.match('/'):
                # Single line comment
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.DIVIDE, '/')
        elif c == '%':
            self.add_token(TokenType.MODULO, '%')
        elif c == '(':
            self.add_token(TokenType.LPAREN, '(')
        elif c == ')':
            self.add_token(TokenType.RPAREN, ')')
        elif c == '{':
            self.add_token(TokenType.LBRACE, '{')
        elif c == '}':
            self.add_token(TokenType.RBRACE, '}')
        elif c == ';':
            self.add_token(TokenType.SEMICOLON, ';')
        elif c == ',':
            self.add_token(TokenType.COMMA, ',')
        elif c == '=':
            if self.match('='):
                self.add_token(TokenType.EQUAL, '==')
            else:
                self.add_token(TokenType.ASSIGN, '=')
        elif c == '!':
            if self.match('='):
                self.add_token(TokenType.NOT_EQUAL, '!=')
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.LESS_EQUAL, '<=')
            else:
                self.add_token(TokenType.LESS_THAN, '<')
        elif c == '>':
            if self.match('='):
                self.add_token(TokenType.GREATER_EQUAL, '>=')
            else:
                self.add_token(TokenType.GREATER_THAN, '>')
        elif c.isdigit():
            self.number()
        elif c.isalpha() or c == '_':
            self.identifier()
        else:
            raise SyntaxError(f"Unexpected character '{c}' at line {self.line}, column {self.column}")

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type, text)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        # Look for decimal part
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # consume '.'
            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        self.column += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def add_token(self, token_type: TokenType, value):
        self.tokens.append(Token(token_type, value, self.line, self.column - len(str(value))))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)


def scan_file(filename: str):
    """Read and scan a file, returning tokens"""
    with open(filename, 'r') as f:
        source = f.read()

    scanner = Scanner(source)
    return scanner.scan_tokens()

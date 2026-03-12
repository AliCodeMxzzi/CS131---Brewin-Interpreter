from brewparse import parse_program
from element import *
from intbase import *

class Interpreter(InterpreterBase):

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.variables = {}

    def run(self, program):
        ast = parse_program(program)
        self.variables = {}
        if ast and ast.elem_type == "program":
            if "functions" in ast.dict:
                # Citation: The following code was written by ChatGPT
                main_function = next((func for func in ast.dict["functions"] if func.dict.get("name") == "main"), None)
                # End of copied code
                if main_function:
                    self.run_func(main_function)
                else:
                    super().error(ErrorType.NAME_ERROR, "No main() function was found")
    
    def run_func(self, func_node):        
        for statement in func_node.dict["statements"]:
            self.run_statement(statement)

    def run_statement(self, statement_node):
        if statement_node.elem_type == "vardef":
            self.do_definition(statement_node)
        elif statement_node.elem_type == "=":
            self.do_assignment(statement_node)
        elif statement_node.elem_type == "fcall":
            self.do_func_call(statement_node)
    
    def do_definition(self, definition_node):
        variable_name = definition_node.dict["name"]
        if variable_name in self.variables:
            super().error(ErrorType.NAME_ERROR, f"Variable {variable_name} defined more than once")
        else:
            self.variables[variable_name] = None

    def do_assignment (self, assignment_node):
        variable_name = assignment_node.dict["name"]
        if variable_name not in self.variables:
            super().error(ErrorType.NAME_ERROR, f"Variable {variable_name} has not been defined")
        value = self.evaluate_expression(assignment_node.dict["expression"])
        self.variables[variable_name] = value

    def do_func_call (self, fcall_node):
        function_name = fcall_node.dict["name"]
        if function_name == "print":
            self.do_print(fcall_node)
        elif function_name == "inputi":
            self.do_inputi(fcall_node)
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {function_name} has not been defined.")

    def evaluate_expression(self, expression_node):
        # Citation: The following code was written by ChatGPT
        OPERATIONS = {"+": lambda x, y: x + y, "-": lambda x, y: x - y}
        # End of copied code
        
        if expression_node.elem_type == "var":
            variable_name = expression_node.dict["name"]
            if variable_name not in self.variables:
                super().error(ErrorType.NAME_ERROR, f"Variable {variable_name} has not been defined")
            return self.variables[variable_name]
        
        elif expression_node.elem_type in ["int", "string"]:
            return expression_node.dict["val"]
        
        elif expression_node.elem_type in OPERATIONS:
            return self.do_operation(expression_node, OPERATIONS)
        
        elif expression_node.elem_type == "fcall":
            return self.do_inputi(expression_node)

    def do_print(self, print_node):
        args = [str(self.evaluate_expression(arg)) for arg in print_node.dict["args"]]
        super().output("".join(args))
    
    def do_inputi(self, input_node):
        args = input_node.dict["args"]
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "No inputi() function found that takes > 1 parameter")
        else:
            if args:
                prompt = self.evaluate_expression(args[0])
                super().output(prompt)
            
            user_input = int(super().get_input())
            return user_input
        
    def do_operation(self, expression_node, operations):    
        op1 = self.evaluate_expression(expression_node.dict["op1"])
        op2 = self.evaluate_expression(expression_node.dict["op2"])

        if not isinstance(op1, int) or not isinstance(op2, int):
            super().error(ErrorType.TYPE_ERROR, "Incompatible types for arithmetic operation")
            return None

        return operations[expression_node.elem_type](op1, op2)
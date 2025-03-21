import print_error

class ErrorLogger:
    """Logs constraint violations"""
    def log_constraint_error(self, constraint_type: str, description: str) -> None:
        #print(f"Constraint Error: {constraint_type} - {description}")
        print_error.log_constraint_error(constraint_type, description)

    # Logs fatal errors
    def log_fatal_error(self, constraint_type: str, description: str) -> None:
        print(f"FATAL ERROR: {constraint_type} - {description}")

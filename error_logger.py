class ErrorLogger:
    def log_constraint_error(self, constraint_type: str, description: str) -> None:
        """Logs constraint violations"""
        print(f"Constraint Error: {constraint_type} - {description}")

    def log_fatal_error(self, constraint_type: str, description: str) -> None:
        """Logs fatal errors"""
        print(f"FATAL ERROR: {constraint_type} - {description}")

class SmartRiskError(Exception):
    def __init__(self, message: str, code: str = "GENERIC_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.code}] {self.message}"


class AuthError(SmartRiskError):
    def __init__(self, message: str):
        super().__init__(message, code="AUTH_ERROR")


class ValidationError(SmartRiskError):
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class DataError(SmartRiskError):
    def __init__(self, message: str):
        super().__init__(message, code="DATA_ERROR")


class SimulationError(SmartRiskError):
    def __init__(self, message: str):
        super().__init__(message, code="SIMULATION_ERROR")

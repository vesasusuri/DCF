class DomainError(Exception):
    """Base class for domain-level errors."""


class ProjectNotFoundError(DomainError):
    def __init__(self, project_id: str) -> None:
        super().__init__(f"Project not found: {project_id}")
        self.project_id = project_id


class InvalidAssumption(DomainError):
    pass


class RunNotFoundError(DomainError):
    pass


class AuditViolation(DomainError):
    pass


class UserNotFoundError(DomainError):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"User not found: {user_id}")
        self.user_id = user_id


class NotPortfolioManagerError(DomainError):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"User is not a portfolio manager: {user_id}")
        self.user_id = user_id


class DuplicateAssignmentError(DomainError):
    def __init__(self, project_id: str, user_id: str) -> None:
        super().__init__(f"Portfolio manager already assigned to project: {project_id}")
        self.project_id = project_id
        self.user_id = user_id


class AssignmentNotFoundError(DomainError):
    def __init__(self, project_id: str, user_id: str) -> None:
        super().__init__(f"Portfolio manager assignment not found for project {project_id}")
        self.project_id = project_id
        self.user_id = user_id


class UserAlreadyExistsError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"User already exists: {email}")
        self.email = email

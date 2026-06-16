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

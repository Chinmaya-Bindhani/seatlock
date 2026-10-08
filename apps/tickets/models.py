from django.db import models
import uuid
from django.conf import  settings
from django.core.validators import MaxLengthValidator,MinLengthValidator


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN","Open"
        IN_PROGRESS = "IN_PROGRESS","In progress"
        RESOLVED = "RESOLVED","Resolved"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    title = models.CharField(max_length=200)

    description = models.TextField(validators=[MinLengthValidator(10),MaxLengthValidator(10_000)])

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tickets"

    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_tickets",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.OPEN
    )


    version = models.PositiveIntegerField(default=1)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    resolved_at = models.DateTimeField(
        null= True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]

        indexes = [
            models.Index(
                fields=["customer", "-created_at", "-id"],
                name="ticket_customer_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at", "-id"],
                name="ticket_status_created_idx",
            ),
            models.Index(
                fields=["assignee", "status", "-created_at", "-id"],
                name="ticket_agent_status_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(
                            status="OPEN",
                            assignee__isnull=True,
                        )
                        | models.Q(
                    status__in=["IN_PROGRESS", "RESOLVED"],
                    assignee__isnull=False,
                )
                ),
                name="ticket_status_assignment_valid",
            ),
            models.CheckConstraint(
                condition=(
                        models.Q(
                            status="RESOLVED",
                            resolved_at__isnull=False,
                        )
                        | models.Q(
                    status__in=["OPEN", "IN_PROGRESS"],
                    resolved_at__isnull=True,
                )
                ),
                name="ticket_resolution_time_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="ticket_version_positive",
            ),
        ]

    def __str__(self):
        return self.title

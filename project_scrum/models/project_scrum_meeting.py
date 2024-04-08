# Copyright <2017> <Tenovar Ltd>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ProjectScrumMeeting(models.Model):
    _name = "project.scrum.meeting"
    _description = "Project Scrum Daily Meetings"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        ondelete="cascade",
        index=True,
        tracking=True,
        change_default=True,
        required=True,
    )
    sprint_id = fields.Many2one(
        comodel_name="project.scrum.sprint",
        string="Sprint",
    )
    datetime_meeting = fields.Datetime(
        string="Date and Time of the meeting",
        required=True,
    )
    user_id_meeting = fields.Many2one(
        comodel_name="res.users",
        string="Meeting Organizer",
        required=True,
        default=lambda self: self.env.user,
    )
    question_yesterday = fields.Html(
        string="Description Yesterday",
        required=True,
    )
    question_today = fields.Html(
        string="Description Today",
        required=True,
    )
    question_blocks = fields.Html(
        string="Description",
        required=False,
    )
    question_backlog = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Backlog Accurate?",
        required=False,
        default="yes",
    )
    company_id = fields.Many2one(
        related="project_id.company_id",
    )

    @api.depends(
        "project_id",
        "project_id.name",
        "user_id_meeting.name",
        "datetime_meeting",
    )
    def _compute_display_name(self):
        for rec in self:
            if rec.project_id:
                rec.display_name = (
                    f"{rec.project_id.name}"
                    f" - {rec.user_id_meeting.name}"
                    f" - {rec.datetime_meeting}"
                )
            else:
                rec.display_name = (
                    f"{rec.user_id_meeting.name}"
                    f" - {rec.datetime_meeting}"
                )

    def send_email(self):
        self.ensure_one()
        template = self.env.ref("project_scrum.email_template_id", False)
        compose_form = self.env.ref(
            "mail.email_compose_message_wizard_form",
            False,
        )
        ctx = dict(
            default_model="project.scrum.meeting",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode="comment",
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

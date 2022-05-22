from flask import Blueprint, request
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from marshmallow import ValidationError

from .schema import AssignmentGradeSchema, AssignmentSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.auth_principal
def list_student_assignments(p):
    """Returns list of all assignments cerated by a student"""
    student_assignments = Assignment.get_assignments_by_student(p.student_id)
    assignments_dump = AssignmentSchema().dump(student_assignments, many=True)
    return APIResponse.respond(data=assignments_dump)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.auth_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment_id = grade_assignment_payload.id
    assignment_grade = grade_assignment_payload.grade
    if assignment_grade not in ['A','B','C','D']:
        return {"error" : "ValidationError"},400
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return {"error" : "FyleError"},404
    if assignment.teacher_id != p.teacher_id:
        return {"error": "FyleError"}, 400
    assignment.grade = assignment_grade
    assignment.state = AssignmentStateEnum.GRADED
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=graded_assignment_dump)
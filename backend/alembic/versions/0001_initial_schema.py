"""Initial schema for Talent Discovery

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='employee', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. employee_profiles
    op.create_table(
        'employee_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('employee_code', sa.String(length=40), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('designation', sa.String(length=100), nullable=False),
        sa.Column('years_of_experience', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('education', sa.String(length=255), server_default='', nullable=False),
        sa.Column('location', sa.String(length=100), server_default='', nullable=False),
        sa.Column('bio', sa.Text(), server_default='', nullable=False),
        sa.Column('resume_url', sa.String(length=500), server_default='', nullable=False),
        sa.Column('profile_completion', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_code'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_employee_profiles_department'), 'employee_profiles', ['department'], unique=False)
    op.create_index(op.f('ix_employee_profiles_employee_code'), 'employee_profiles', ['employee_code'], unique=True)
    op.create_index(op.f('ix_employee_profiles_id'), 'employee_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_employee_profiles_user_id'), 'employee_profiles', ['user_id'], unique=True)

    # 3. skills
    op.create_table(
        'skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_skills_category'), 'skills', ['category'], unique=False)
    op.create_index(op.f('ix_skills_id'), 'skills', ['id'], unique=False)
    op.create_index(op.f('ix_skills_name'), 'skills', ['name'], unique=True)

    # 4. employee_skills
    op.create_table(
        'employee_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('proficiency', sa.Integer(), server_default='1', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('skill_type', sa.String(length=30), server_default='explicit', nullable=False),
        sa.Column('source', sa.String(length=100), server_default='self-reported', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_skills_employee_id'), 'employee_skills', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_skills_id'), 'employee_skills', ['id'], unique=False)
    op.create_index(op.f('ix_employee_skills_skill_id'), 'employee_skills', ['skill_id'], unique=False)

    # 5. skill_evidence
    op.create_table(
        'skill_evidence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_skill_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(length=100), nullable=False),
        sa.Column('source_reference', sa.String(length=255), server_default='', nullable=False),
        sa.Column('evidence_text', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_skill_id'], ['employee_skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_evidence_employee_skill_id'), 'skill_evidence', ['employee_skill_id'], unique=False)
    op.create_index(op.f('ix_skill_evidence_id'), 'skill_evidence', ['id'], unique=False)

    # 6. roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('level', sa.String(length=60), server_default='Mid-Level', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_department'), 'roles', ['department'], unique=False)
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_title'), 'roles', ['title'], unique=False)

    # 7. role_skills
    op.create_table(
        'role_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('required_proficiency', sa.Integer(), server_default='3', nullable=False),
        sa.Column('importance', sa.String(length=30), server_default='high', nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_skills_id'), 'role_skills', ['id'], unique=False)
    op.create_index(op.f('ix_role_skills_role_id'), 'role_skills', ['role_id'], unique=False)
    op.create_index(op.f('ix_role_skills_skill_id'), 'role_skills', ['skill_id'], unique=False)

    # 8. role_matches
    op.create_table(
        'role_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('match_score', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('matching_skills', sa.JSON(), nullable=False),
        sa.Column('missing_skills', sa.JSON(), nullable=False),
        sa.Column('explanation', sa.Text(), server_default='', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_matches_employee_id'), 'role_matches', ['employee_id'], unique=False)
    op.create_index(op.f('ix_role_matches_id'), 'role_matches', ['id'], unique=False)
    op.create_index(op.f('ix_role_matches_role_id'), 'role_matches', ['role_id'], unique=False)

    # 9. skill_gaps
    op.create_table(
        'skill_gaps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('current_proficiency', sa.Integer(), server_default='0', nullable=False),
        sa.Column('required_proficiency', sa.Integer(), server_default='1', nullable=False),
        sa.Column('gap_level', sa.String(length=30), server_default='medium', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_gaps_employee_id'), 'skill_gaps', ['employee_id'], unique=False)
    op.create_index(op.f('ix_skill_gaps_id'), 'skill_gaps', ['id'], unique=False)
    op.create_index(op.f('ix_skill_gaps_role_id'), 'skill_gaps', ['role_id'], unique=False)
    op.create_index(op.f('ix_skill_gaps_skill_id'), 'skill_gaps', ['skill_id'], unique=False)

    # 10. courses
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(length=50), server_default='Intermediate', nullable=False),
        sa.Column('duration', sa.String(length=50), server_default='4 weeks', nullable=False),
        sa.Column('url', sa.String(length=500), server_default='', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)
    op.create_index(op.f('ix_courses_provider'), 'courses', ['provider'], unique=False)
    op.create_index(op.f('ix_courses_skill_id'), 'courses', ['skill_id'], unique=False)

    # 11. course_recommendations
    op.create_table(
        'course_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), server_default='', nullable=False),
        sa.Column('priority', sa.String(length=30), server_default='medium', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employee_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_recommendations_employee_id'), 'course_recommendations', ['employee_id'], unique=False)
    op.create_index(op.f('ix_course_recommendations_id'), 'course_recommendations', ['id'], unique=False)

    # 12. learning_roadmaps
    op.create_table(
        'learning_roadmaps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('target_role_id', sa.Integer(), nullable=True),
        sa.Column('roadmap_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_role_id'], ['roles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_roadmaps_employee_id'), 'learning_roadmaps', ['employee_id'], unique=False)
    op.create_index(op.f('ix_learning_roadmaps_id'), 'learning_roadmaps', ['id'], unique=False)
    op.create_index(op.f('ix_learning_roadmaps_target_role_id'), 'learning_roadmaps', ['target_role_id'], unique=False)

    # 13. external_profiles
    op.create_table(
        'external_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('profile_url', sa.String(length=500), server_default='', nullable=False),
        sa.Column('username', sa.String(length=100), server_default='', nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_external_profiles_employee_id'), 'external_profiles', ['employee_id'], unique=False)
    op.create_index(op.f('ix_external_profiles_id'), 'external_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_external_profiles_platform'), 'external_profiles', ['platform'], unique=False)


def downgrade() -> None:
    op.drop_table('external_profiles')
    op.drop_table('learning_roadmaps')
    op.drop_table('course_recommendations')
    op.drop_table('courses')
    op.drop_table('skill_gaps')
    op.drop_table('role_matches')
    op.drop_table('role_skills')
    op.drop_table('roles')
    op.drop_table('skill_evidence')
    op.drop_table('employee_skills')
    op.drop_table('skills')
    op.drop_table('employee_profiles')
    op.drop_table('users')

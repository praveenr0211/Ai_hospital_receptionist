"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-23 19:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Specialties table
    op.create_table(
        'specialties',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_specialties_name', 'specialties', ['name'])

    # 2. Doctors table
    op.create_table(
        'doctors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('specialty_id', sa.Integer(), nullable=False),
        sa.Column('qualification', sa.String(length=150), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('consultation_fee', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['specialty_id'], ['specialties.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.CheckConstraint("status IN ('active', 'inactive', 'on_leave')", name='chk_doctor_status')
    )
    op.create_index('ix_doctors_name', 'doctors', ['name'])
    op.create_index('ix_doctors_specialty_id', 'doctors', ['specialty_id'])

    # 3. Patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_patients_phone', 'patients', ['phone'])

    # 4. Doctor Schedules table
    op.create_table(
        'doctor_schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('slot_duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id', 'doctor_id', name='uq_schedule_doctor'),
        sa.CheckConstraint('start_time < end_time', name='chk_schedule_time_order'),
        sa.CheckConstraint('slot_duration_minutes > 0', name='chk_slot_duration_positive')
    )
    op.create_index('ix_doctor_schedules_doctor_id', 'doctor_schedules', ['doctor_id'])
    op.create_index('ix_doctor_schedules_date', 'doctor_schedules', ['date'])

    # 5. Appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=False),
        sa.Column('appointment_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='confirmed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', name='fk_appointment_patient'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='RESTRICT', name='fk_appointment_doctor'),
        sa.ForeignKeyConstraint(['schedule_id', 'doctor_id'], ['doctor_schedules.id', 'doctor_schedules.doctor_id'], ondelete='CASCADE', name='fk_appointment_schedule_doctor'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('start_time < end_time', name='chk_appointment_time_order'),
        sa.CheckConstraint("status IN ('pending', 'confirmed', 'cancelled', 'completed', 'no_show')", name='chk_appointment_status')
    )
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('ix_appointments_doctor_id', 'appointments', ['doctor_id'])
    op.create_index('ix_appointments_schedule_id', 'appointments', ['schedule_id'])
    op.create_index('ix_appointments_appointment_date', 'appointments', ['appointment_date'])
    op.create_index('ix_appointments_start_time', 'appointments', ['start_time'])
    
    # Critical Partial Unique Index: Prevent active double-booking
    op.create_index(
        'uq_doctor_active_slot',
        'appointments',
        ['doctor_id', 'appointment_date', 'start_time'],
        unique=True,
        postgresql_where=sa.text("status != 'cancelled'")
    )

    # 6. Calls table
    op.create_table(
        'calls',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('intent', sa.String(length=100), nullable=False),
        sa.Column('specialty_detected', sa.String(length=100), nullable=True),
        sa.Column('outcome', sa.String(length=50), nullable=False, server_default='appointment_booked'),
        sa.Column('escalated', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("outcome IN ('appointment_booked', 'information_provided', 'human_transfer', 'cancelled', 'failed', 'abandoned')", name='chk_call_outcome')
    )
    op.create_index('ix_calls_patient_id', 'calls', ['patient_id'])
    op.create_index('ix_calls_phone_number', 'calls', ['phone_number'])

    # 7. Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=True),
        sa.Column('doctor_id', sa.Integer(), nullable=True),
        sa.Column('channel', sa.String(length=20), nullable=False, server_default='SMS'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('(patient_id IS NOT NULL AND doctor_id IS NULL) OR (patient_id IS NULL AND doctor_id IS NOT NULL)', name='chk_notification_single_recipient'),
        sa.CheckConstraint("channel IN ('SMS', 'WhatsApp', 'Email')", name='chk_notification_channel'),
        sa.CheckConstraint("status IN ('pending', 'sent', 'delivered', 'failed')", name='chk_notification_status')
    )
    op.create_index('ix_notifications_appointment_id', 'notifications', ['appointment_id'])
    op.create_index('ix_notifications_patient_id', 'notifications', ['patient_id'])
    op.create_index('ix_notifications_doctor_id', 'notifications', ['doctor_id'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('calls')
    op.drop_index('uq_doctor_active_slot', table_name='appointments')
    op.drop_table('appointments')
    op.drop_table('doctor_schedules')
    op.drop_table('patients')
    op.drop_table('doctors')
    op.drop_table('specialties')

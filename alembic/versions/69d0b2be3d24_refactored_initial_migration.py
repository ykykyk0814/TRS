"""Refactored Alembic migration using high-level API

Revision ID: 69d0b2be3d24
Revises:
Create Date: 2025-07-09 08:56:57.419018
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision = "69d0b2be3d24"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("TRUE"),
        ),
        sa.Column(
            "is_superuser",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "is_verified",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
        sa.Column("first_name", sa.String),
        sa.Column("last_name", sa.String),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"])

    # Create update_updated_at_column function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )

    # Create user_preferences table
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "prefers_direct_flights",
            sa.Boolean,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "prefers_morning_departure",
            sa.Boolean,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "prefers_evening_departure",
            sa.Boolean,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "prefers_window_seat",
            sa.Boolean,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "prefers_aisle_seat",
            sa.Boolean,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "prefers_business_class",
            sa.Boolean,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "prefers_economy_class",
            sa.Boolean,
            server_default=sa.text("TRUE"),
        ),
        sa.Column(
            "prefers_short_layovers",
            sa.Boolean,
            server_default=sa.text("TRUE"),
        ),
        sa.Column(
            "prefers_specific_airlines",
            sa.Boolean,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "price_sensitive",
            sa.Boolean,
            server_default=sa.text("TRUE"),
        ),
        sa.Column(
            "additional_preferences",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_user_preferences_id", "user_preferences", ["id"])
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"])
    op.create_unique_constraint(
        "unique_user_preference",
        "user_preferences",
        ["user_id"],
    )

    # Create tickets table
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("origin", sa.String, nullable=False),
        sa.Column("destination", sa.String, nullable=False),
        sa.Column("departure_date", sa.Date, nullable=False),
        sa.Column("return_date", sa.Date),
        sa.Column("price", sa.Numeric, nullable=False),
        sa.Column("airline", sa.String),
        sa.Column("flight_duration", sa.Interval),
        sa.Column("stops", sa.Integer),
        sa.Column("seat_class", sa.String),
        sa.Column("link", sa.String),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_tickets_id", "tickets", ["id"])

    # Create api_keys table
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("api_key", sa.String, nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_api_keys_id", "api_keys", ["id"])
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])

    # Add update triggers
    op.execute(
        """
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();

        CREATE TRIGGER update_user_preferences_updated_at
            BEFORE UPDATE ON user_preferences
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();

        CREATE TRIGGER update_tickets_updated_at
            BEFORE UPDATE ON tickets
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();

        CREATE TRIGGER update_api_keys_updated_at
            BEFORE UPDATE ON api_keys
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
    )


def downgrade():
    # Drop triggers first before dropping the function
    op.execute(
        """
        DROP TRIGGER IF EXISTS update_users_updated_at ON users;
        DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
        DROP TRIGGER IF EXISTS update_tickets_updated_at ON tickets;
        DROP TRIGGER IF EXISTS update_api_keys_updated_at ON api_keys;
        """
    )
    op.execute(
        """
        DROP FUNCTION IF EXISTS update_updated_at_column();
        """
    )

    op.drop_index("ix_api_keys_user_id", table_name="api_keys")
    op.drop_index("ix_api_keys_id", table_name="api_keys")
    op.drop_table("api_keys")

    op.drop_index("ix_tickets_id", table_name="tickets")
    op.drop_table("tickets")

    op.drop_constraint("unique_user_preference", "user_preferences", type_="unique")
    op.drop_index("ix_user_preferences_user_id", table_name="user_preferences")
    op.drop_index("ix_user_preferences_id", table_name="user_preferences")
    op.drop_table("user_preferences")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

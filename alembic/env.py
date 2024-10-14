from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Импортируйте вашу базу данных и модели
from app.db.db import Base  # Ваш базовый класс
from app.models.user import User  # Ваши модели (например, User)
from app.models.task import Task  # Ваши модели (например, Task)

# Загрузка конфигурации Alembic
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Установите метаданные для автоматической генерации миграций
target_metadata = Base.metadata

# Функции для миграции
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

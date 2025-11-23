FROM postgres:16

RUN apt-get update && \
    apt-get install -y python3 python3.13-venv curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python3 -m venv /opt/patroni-venv

# Активация venv и установка Patroni
RUN /opt/patroni-venv/bin/pip install --no-cache-dir "patroni[etcd]"

# Добавляем venv в PATH (опционально, или вызывать напрямую)
ENV PATH="/opt/patroni-venv/bin:$PATH"

COPY patroni.yml /etc/patroni/patroni.yml
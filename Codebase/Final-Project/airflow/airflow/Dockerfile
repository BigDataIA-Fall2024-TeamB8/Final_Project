FROM apache/airflow:2.7.0

USER root

# Install necessary system dependencies (Firefox, Chrome, ChromeDriver)
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm ./google-chrome-stable_current_amd64.deb && \
    CHROME_DRIVER_VERSION="130.0.6686.4" && \
    wget -N https://storage.googleapis.com/chrome-for-testing-public/$CHROME_DRIVER_VERSION/linux64/chromedriver-linux64.zip -P /tmp && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -r /usr/local/bin/chromedriver-linux64 && \
    rm /tmp/chromedriver-linux64.zip && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Ensure database initialization and webserver startup
RUN airflow db init

CMD ["bash", "-c", "airflow scheduler & airflow webserver"]

# -*- coding: utf-8 -*-
"""Architectural_Diagram.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Mghzgj3u2EI-W7cRS93q6ZGoSx98bBHm
"""

!pip install diagrams
!apt-get install -y graphviz

from google.colab import files
uploaded = files.upload()

pip install diagrams --upgrade

from diagrams import Diagram, Cluster
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3
from diagrams.aws.security import WAF  # Using WAF for JWT Auth placeholder
from diagrams.aws.compute import ECS  # Using ECS for FastAPI placeholder
from diagrams.custom import Custom
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.client import User
from diagrams.programming.framework import Fastapi
from diagrams.generic.compute import Rack as SwaggerUI
from diagrams.generic.compute import Rack as JWTAuth

# Create the architecture diagram
with Diagram("Data Architecture with Clusters", show=True):

    # Define the first cluster (Data Ingestion and Workflow)
    with Cluster("Data Ingestion and Workflow"):
        # Components
        faang_dataset = Custom("FAANG Dataset", "stock.png")
        reddit_posts = Custom("Reddit FAANG Posts", "reddit.png")
        news_articles = Custom("News Articles", "news.png")
        airflow = Airflow("Apache Airflow")
        s3_bucket = S3("AWS S3 Bucket")

        # Data flow
        faang_dataset >> airflow
        reddit_posts >> airflow
        news_articles >> airflow
        airflow >> s3_bucket

    # Define the second cluster (Processing Cluster)
    with Cluster("Processing Cluster"):
        # Components
        sql_server = RDS("SQL Server (User Credentials)")
        jwt_auth = JWTAuth("JWT Auth")
        fastapi = Fastapi("FastAPI")
        swagger_ui = SwaggerUI("Swagger UI")
        pinecone = Custom("Pinecone Vector Database", "Pinecone.png")

        # Data flow within Processing Cluster
        sql_server >> jwt_auth
        jwt_auth >> fastapi
        fastapi >> pinecone
        swagger_ui >> fastapi

    # Define the third cluster (UI Cluster)
    with Cluster("UI Cluster"):
        # Components
        streamlit_ui = Custom("Streamlit/Coagents UI", "streamlit.png")
        user = User("User")
        openai = Custom("OpenAI", "openai.png")

        # Data flow within UI Cluster
        streamlit_ui >> user
        streamlit_ui >> openai

    # Cross-cluster connections
    s3_bucket >> fastapi
    pinecone >> streamlit_ui
    faang_dataset >> pinecone
    reddit_posts >> pinecone
    news_articles >> pinecone

from IPython.display import Image, display
display(Image(filename="/content/data_architecture_with_clusters.png"))

# Base image
FROM python:3-slim
# Create app directory
WORKDIR /usr/src/app
# Install app dependencies
RUN pip install python-dotenv
# Copy only the app.py file
COPY src/app.py ./app.py
# Run the app
CMD [ "python", "-u", "app.py" ]
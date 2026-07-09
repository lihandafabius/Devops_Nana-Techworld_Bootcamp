FROM openjdk:21-jdk-slim
EXPOSE 8080
RUN mkdir /opt/app
COPY app.jar /opt/app/app.jar
WORKDIR /opt/app
CMD ["java","-jar","app.jar"]
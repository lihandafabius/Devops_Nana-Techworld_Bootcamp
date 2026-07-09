FROM openjdk:17.0.2-jdk
EXPOSE 8080
RUN mkdir /opt/app
COPY build/libs/java-app-1.0.1.jar /opt/app/app.jar
WORKDIR /opt/app
CMD ["java","-jar","app.jar"]
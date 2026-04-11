FROM eclipse-temurin:17-jdk-alpine

RUN mkdir -p /home/java-app

WORKDIR /home/java-app 

COPY build/libs/*.jar app.jar   

ENTRYPOINT ["java", "-jar", "app.jar"]

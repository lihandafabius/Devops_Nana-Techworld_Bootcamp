FROM eclipse-temurin:21-jre-jammy
WORKDIR /opt/app
COPY build/libs/java-app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
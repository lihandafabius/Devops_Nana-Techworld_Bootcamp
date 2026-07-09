FROM eclipse-temurin:21-jre-jammy
EXPOSE 8080
RUN mkdir /opt/app
COPY app.jar /opt/app/app.jar
WORKDIR /opt/app
CMD ["java","-jar","app.jar"]
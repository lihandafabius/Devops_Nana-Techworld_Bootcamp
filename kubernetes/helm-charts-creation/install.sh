helm install rediscart ./charts/redis -f values/redis-values.yaml

helm install cartservice ./charts/microservices -f values/cart-service-values.yaml
helm install checkoutservice ./charts/microservices -f values/checkout-service-values.yaml
helm install currencyservice ./charts/microservices -f values/currency-service-values.yaml
helm install paymentservice ./charts/microservices -f values/payment-service-values.yaml
helm install productcatalogservice ./charts/microservices -f values/productcatalog-service-values.yaml
helm install emailservice ./charts/microservices -f values/email-service-values.yaml
helm install recommendationservice ./charts/microservices -f values/recommendation-service-values.yaml
helm install shippingservice ./charts/microservices -f values/shipping-service-values.yaml
helm install frontendservice ./charts/microservices -f values/frontend-values.yaml


---
title: "Networking / Container Gateway"
---

Networking is a crucial aspect of any modern application. In Salad, it is particularly important to have a good understanding of two types of networking requests: outbound and inbound. Outbound networking involves sending data from your application to other APIs or services, while inbound networking involves receiving https requests by your application from other servers or services.

## Outbound Network Requests

When your application runs on a Salad node, it will have the ability to make any outbound requests using the residential IP address of the selected node. This means that your application will have the ability to access websites and other online resources using a different IP address than your server, which can be particularly useful for tasks such as web scraping and online market research. Additionally, because the IP address is associated with a residential location rather than a datacenter, your requests are less likely to be blocked or flagged as suspicious, enhancing the reliability and effectiveness of your application. Overall, running your application on a Salad node provides a powerful tool for accessing online resources and conducting online research in a more efficient and effective manner.

### Outbound Networking Information

- The IP address will be the residential IP address of the particular node running your application
- The hostname will be set to the unique Salad machine id, this is the same value as the `SALAD_MACHINE_ID` environment variable.

## Inbound Network Requests

If your application needs to receive http requests from external services, Salad provides a simple networking solution that will automatically load balance the inbound requests across all the container instances running within a specific container group. This feature is particularly useful for applications that require high availability and scalability. Furthermore, load balancing ensures that incoming requests are distributed evenly across all instances, which in turn improves the overall performance of the application, reduces latency, and prevents any one instance from becoming overloaded. With Salad's Container Gateway solution, you can rest assured that your application will be able to handle a large volume of traffic without encountering any issues related to scalability or availability.

Each container group can be configured to include inbound networking via the Container Gateway feature. For each container group, you will need to specify the port that your application uses to handle http requests. This is necessary to ensure that Salad can automatically create a static URL with a load balancer, which allows you to send requests directly to your container group. As you scale your container group up or down, Salad will automatically manage the load balancer, allowing you scale without additional configuration. Additionally, your container will need to accept IPv6 connections. To test and if needed enable IPv6 connections, see [Sending authenticated requests to your container](doc:sending-requests)

We support options for both authenticated (recommended) and unauthenticated networking. If authentication is selected, you must include your Salad API key when making requests to your application, see [Sending authenticated requests to your container](doc:sending-requests). If authentication is not selected, any traffic to the domain name will go to your container. In this case authentication should be completed by your container.

> 📘 Requesting a unique URL for each node
>
> Create container groups with only one replica each. Because each container group has a unique URL assigned to it, this approach allows you to uniquely address each node. To manage large numbers of nodes/replicas, we recommend using the API.

### Container Gateway Requirements

- Your application must bind to IPv4 (a WSL2 limitation) and IPv6 (for load balancing)
- All requests to the Salad load balancer must be over HTTPS

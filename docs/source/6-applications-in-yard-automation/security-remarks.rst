Security in helyOS Framework
============================

The design of the helyOS framework takes into consideration several potential threats for applications in autonomous driving within a multi-vendor environment. In this chapter, we address these threats and present our mitigation strategies.

MITM on helyOS Core and Data Exposure
-------------------------------------

**Target:** External Apps

To mitigate Man-In-The-Middle (MITM) attacks on the helyOS core and prevent data exposure, you should utilize SSL for HTTPS via a server-proxy. Additionally, deploying a load-balancer or web server (e.g., nginx) helps secure connections effectively.

MITM on RabbitMQ Server and Data Exposure
-----------------------------------------

**Target:** Agents & External Apps

To protect against MITM attacks on the RabbitMQ server and ensure data security, you should enable SSL for AMQPS/MQTTS. RabbitMQ's support for TLS in AMQP and MQTT protocols further enhances the encryption of data transmission.

Imposter Agent via Stolen Credentials
-------------------------------------

**Target:** helyOS core & Agents

To prevent imposter agents from using stolen credentials, you can activate RabbitMQ's **verify_peer** feature to ensure authenticated and secure communication between agents and the helyOS core. However, once verify_peer is enabled, certificates must be created for each one of the agent, and the certificate authority file for each agent must be loaded into the RabbitMQ server.
This approach **does not solve the problem of message tampering**, where an authenticated agent might send malicious commands to another agent. For AMQP only, you can mitigate this risk by combining the **verify_peer** method with RabbitMQ's `user_id` validation (`validated-user-id`_ ) and implementing a whitelist in the receptors. This combination  ensure that only messages from authenticated agents from the correct origin are executed.

.. _validated-user-id: https://www.rabbitmq.com/docs/validated-user-id

Imposter Agent via Stolen Credentials + Message Tampering
----------------------------------------------------------

**Target:** helyOS core & Agents

In scenarios where imposter or valid agents might tamper with messages using stolen credentials, you can sign messages with RSA keys and implement a whitelist in the receptors. The helyOS core distributes RSA public keys to verify message authenticity.  
This method ensures both authenticity of the agent and message origin,  such that agents cannot produce tampered messages, as verification occurs upon message reception.

Unexpected Messages from Devices
-------------------------------------------------------

**Target:** helyOS core & Agents

To handle unexpected messages from devices (for example, from different vendors), restrict routing permissions in RabbitMQ for specific agents via the dashboard. For instance, limit certain agents to communicate solely with the helyOS core, thereby preventing unauthorized message flows.

Message Flooding by Agents
--------------------------

**Target:** helyOS core & Agents

To prevent message flooding by agents, we set `MESSAGE_RATE_LIMIT` and `MESSAGE_UPDATE_LIMIT`. If an agent exceeds the publishing limit, it leads to the agent's disconnection, ensuring the helyOS core remains stable and responsive.

MITM on Microservice Core and Data Exposure
--------------------------------------------

**Target:** Application Data

To protect against MITM attacks on the microservices and prevent data exposure, deploy microservices on a firewall or private network. If a microservice is accessible via a public network, setting HTTPS on the microservice side can encrypt communication, although the helyOS core cannot yet validate the microservice hostname using certificate authority validation.

Misuse of AGENT_REGISTRATION_TOKEN in Production
-------------------------------------------------

**Target:** helyOS core & Agents

Auto registration of agents is a feature to facilitate the development, it should not be used in production. To prevent the misuse of `AGENT_REGISTRATION_TOKEN` in production environments, we remove the token and delete the RabbitMQ `anonymous` account. Furthermore, we ensure that the RabbitMQ guest account is removed, enhancing overall system security.
Welcome to the OpenShift IAM Pod Identity Broker
================================================

This project contains code and configuration suitable for providing IAM pod identities and temporary, STS credentials
to OpenShift 4.2+ using a sidecar proxy and Lambda-based API. It borrows concepts from [kiam][1] and the
[amazon-eks-pod-identity-webhook][2].

What's Here
-----------

This sample includes:

* README.md - this file
* [User Guide.pdf][3] - Walks through installation, validation and usage of the OCP IAM Broker & Webhook
  * The [user guide](./user_guide.adoc) can also be found in Asciidoc format
* assets/broker-webhook/cloudformation/deployment.yml - CloudFormation facilitating the AWS portion of deployment
* assets/proxy/* - Dockerfile and S2I artifacts for building proxy images for use on OCP

What Do I Do Next?
------------------

Please review the User Guide.

[1]: https://github.com/uswitch/kiam
[2]: https://github.com/aws/amazon-eks-pod-identity-webhook
[3]: User%20Guide.pdf

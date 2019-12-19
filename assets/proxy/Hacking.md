Local Proxy Development
=======================
Building & running the proxy container locally will allow you to validate the broker. It
still requires the broker configuration/deployment and connectivity between the
local workstation and the deployed broker endpoint.

Building Locally
----------------

Local container builds should be achievable from either Docker or podman/buildah.

<pre>
[proxy]$ buildah build-using-dockerfile ./
STEP 1: FROM registry.access.redhat.com/ubi8/ubi:latest
STEP 2: LABEL maintainer=""
STEP 3: EXPOSE 53080
STEP 4: COPY nginx.conf.TEMPLATE /etc/nginx/nginx.conf.TEMPLATE
STEP 5: COPY docker-entrypoint.sh ./docker-entrypoint.sh
STEP 6: ENTRYPOINT ["./docker-entrypoint.sh"]
STEP 7: CMD ["nginx", "-g", "daemon off;"]
STEP 8: COMMIT
Getting image source signatures
Copying blob 831c5620387f done
Copying blob ce342cf1241f done
Copying blob e993d2bfe958 done
Copying blob 64ba105edc18 done
Copying config 79c4456849 done
Writing manifest to image destination
Storing signatures
79c445684917eaa8f61c2902f499669052c868b5605c650968d6fa54a02bc4c9
</pre>

Running Locally
---------------

The environment variable <code>OCP_BROKER_LOC</code> must be set to the deployed
broker endpoint. In addition, the AWS ECS metadata environment variables must
be set.

<pre>
[proxy]$ setsebool -P httpd_can_network_connect 1
[proxy]$ podman run -dt 
    -p 53080:53080/tcp 
    -e OCP_BROKER_LOC=https://MYAPI.execute-api.us-east-2.amazonaws.com/Prod 
    79c445811ff
</pre>



<h3>Example usage output</h3>

Assuming you've successfully stood up the broker and registered an AWS role
to be delegated by the AWS_CONTAINER_AUTHORIZATION_TOKEN above, locally, the 
credentials will be able to be fetched and used by the AWS CLI/SDK.

<pre>
[proxy]$ export AWS_CONTAINER_CREDENTIALS_FULL_URI=http://127.0.0.1:53080/
[proxy]$ export AWS_CONTAINER_AUTHORIZATION_TOKEN=XYZABC
[proxy]$ aws s3 ls
2019-04-17 07:14:48 cf-templates-7gxyzsc6jj-us-east-1
2019-02-20 10:37:46 cf-templates-7gxyzsc6jj-us-east-2
2019-05-13 14:13:28 cf-templates-7gxyzsc6jj-us-west-2
</pre>
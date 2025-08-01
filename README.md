# BRATS_2020

## **How to run this tutorial (with/without TLS with Federated Runtime as a simulation):**

### 1. If you haven't done so already, create a virtual environment, install OpenFL, and upgrade pip:
  - For help with this step, visit the "Install the Package" section of the [OpenFL installation instructions](https://openfl.readthedocs.io/en/latest/installation.html).

# Generate Certificates:
These commands are not supported with fx experimental. 

**Ref:** https://github.com/securefederatedai/openfl/blob/3c15a86d8c7156e740ca2912071bc6fcd7b6149b/docs/developer_guide/utilities/pki.rst#id7

## Director
```sh
fx pki install -p certs --ca-url localhost:50050
fx pki run -p certs
fx pki get-token -n localhost --ca-path certs --ca-url localhost:50050
cd director
fx pki certify -n localhost -t `director_token`
```

## Envoy-1
```sh
fx pki get-token -n Apollo --ca-path certs --ca-url localhost:50050
cd Apollo
fx pki certify -n Apollo -t `apollo_token`
```

## Envoy-2
```sh
fx pki get-token -n Sparsh --ca-path certs --ca-url localhost:50050
cd Sparsh
fx pki certify -n Sparsh -t `sparsh_token`
```

## Workspace
```sh
fx pki get-token -n experiment --ca-path certs --ca-url localhost:50050
cd workspace
fx pki certify -n experiment -t `experiment_token`
```
</br>

# Building a workspace image

OpenFL supports `Gramine-based <https://gramine.readthedocs.io/en/stable/>` TEEs that run within SGX.

```sh
docker build -t brats_test -f brats_fl.dockerfile .
```

This command builds the base image and a TEE-ready workspace image.

**Note:** In the current demo configuration, only the director component is set up to run inside Docker with gramine-sgx. To enable collaborator nodes to run with Gramine TEE support, the collaborator and the workspace directories need to be copied into the Dockerfile and the container can then be executed with Gramine protection. 


# Dataset Preprocessing

Dataset URL:

Note: There is minor issue with the dataset for the entry 

### 1. Split terminal into 4 (1 terminal for the director, 2 for the envoys, and 1 for the experiment)

### 2. Do the following in each terminal:
   - Activate the virtual environment from step 1:
   
```sh
source venv/bin/activate
```

### 3. In the first terminal, activate experimental features and run the director:

### Aggregator

### Running without a TEE
Using the native ``fx`` command within the image will run the experiment without TEEs.

```sh
docker run -u 1000:1000 -v $HOME/.metaflow:/intel/.metaflow  -it --net=host --device=/dev/sgx_enclave --device /dev/sgx_provision --security-opt no-new-privileges brats_test director start -c director/director_config.yaml -rc director/cert/root_ca.crt -pk director/cert/localhost.key -oc director/cert/localhost.crt
```

## Running within a TEE
To run ``fx`` within a TEE, mount the SGX device and AESMD volumes. In addition, prefix the ``fx`` command with the ``gramine-sgx`` directive.

### Aggregator
```sh
docker run -u 1000:1000 -e GRAMINE=1 -v $HOME/.metaflow:/intel/.metaflow  -it --net=host --device=/dev/sgx_enclave --device /dev/sgx_provision --security-opt no-new-privileges brats_test director start -c director/director_config.yaml -rc director/cert/root_ca.crt -pk director/cert/localhost.key -oc director/cert/localhost.crt
```

### 4. In the second, and third terminals, run the envoys:

#### 4.1 Second terminal
```sh
cd Apollo
./start_envoy.sh
```

#### 4.2 Third terminal
```sh
cd Sparsh
./start_envoy.sh
```

### 5. Now that your director and envoy terminals are set up, run the Jupyter Notebook in your experiment terminal:

```sh
cd workspace
jupyter lab brats_2020.ipynb
```
- A Jupyter Server URL will appear in your terminal. In your browser, proceed to that link. Once the webpage loads, click on the pytorch_tinyimagenet.ipynb file. 
- To run the experiment, select the icon that looks like two triangles to "Restart Kernel and Run All Cells". 
- You will notice activity in your terminals as the experiment runs, and when the experiment is finished the director terminal will display a message that the experiment has finished successfully.

**Note:** 
Alternatively, this workflow can be executed in a native environment without Docker containerization using the Federated Learning Workflow API.

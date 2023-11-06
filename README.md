# Serverless WhisperX: Speech-to-Text with KEDA and Dapr on Kubernetes  
   
This repository demonstrates how to deploy a serverless speech-to-text application using OpenAI's Whisper, Kubernetes-based Event Driven Autoscaling (KEDA), and Dapr on a Kubernetes cluster. The application processes audio files, transcribes them using Whisper, and outputs the transcriptions with word-level timestamps and speaker diarization.  
   
## Table of Contents  
   
- [Overview](#overview)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Troubleshooting](#troubleshooting)  
- [License](#license)  
   
## Overview  
   
The Serverless WhisperX application comprises three main components:  
   
1. **WhisperX**: A custom container with a worker that retrieves audio files from an Azure Storage Queue, transcribes them using OpenAI's Whisper ASR API, and stores the transcriptions with word-level timestamps and speaker diarization.  
2. **KEDA**: Kubernetes-based Event Driven Autoscaling (KEDA) is a component that provides event-driven autoscaling for every container in Kubernetes. KEDA monitors the Azure Storage Queue and scales the WhisperX worker based on the number of messages in the queue.  
3. **Dapr**: Dapr is a portable, event-driven runtime that makes it easy for developers to build resilient, microservice stateless and stateful applications that run on the cloud and edge. In this application, Dapr is used to manage the connection to Azure Storage Queue.  
   
## Prerequisites  
   
Before you begin, you need to have the following installed and set up:  
   
- [Docker](https://docs.docker.com/get-docker/)  
- Kubernetes cluster (e.g., [AKS](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes), [GKE](https://cloud.google.com/kubernetes-engine/docs), [EKS](https://aws.amazon.com/eks/), or [Minikube](https://minikube.sigs.k8s.io/docs/start/))  
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)  
- [Helm](https://helm.sh/docs/intro/install/) (optional, for installing KEDA and Dapr)  
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (optional, for installing KEDA and Dapr on AKS)  
   
## Installation  
   
1. Clone this repository:  
  
   ```  
   git clone https://github.com/zecloud/Serverless-whisperx.git  
   cd Serverless-whisperx  
   ```  
   
2. Install KEDA and Dapr on your Kubernetes cluster.  
  
   For KEDA, use Helm:  
  
   ```  
   helm repo add kedacore https://kedacore.github.io/charts  
   helm repo update  
   kubectl create namespace keda  
   helm install keda kedacore/keda --namespace keda  
   ```  
  
   Or, for AKS, use the Azure CLI:  
  
   ```  
   az aks update --resource-group <resource-group> --name <cluster-name> --enable-keda  
   ```  
  
   For Dapr, use Helm:  
  
   ```  
   helm repo add dapr https://dapr.github.io/helm-charts/  
   helm repo update  
   kubectl create namespace dapr-system  
   helm install dapr dapr/dapr --namespace dapr-system  
   ```  
  
   Or, for AKS, use the Azure CLI:  
  
   ```  
   az k8s-extension create --cluster-type managedClusters --cluster-name <cluster-name> --resource-group <resource-group> --name dapr --extension-type Microsoft.Dapr  
   ```  
   
3. Apply the `keda.yaml` and `daprcomponent.yaml` files to your cluster:  
  
   ```  
   kubectl apply -f keda.yaml  
   kubectl apply -f daprcomponent.yaml  
   ```  
   
4. Build the Docker image and push it to your container registry:  
  
   ```  
   docker build -t <your-registry>/<image-name>:latest .  
   docker push <your-registry>/<image-name>:latest  
   ```  
   
## Configuration  
   
1. Update the `daprcomponent.yaml` file with your Azure Storage Queue connection string:  
  
   ```  
   apiVersion: dapr.io/v1alpha1  
   kind: Component  
   metadata:  
     name: whisperx-queue  
   spec:  
     type: bindings.azure.storagequeues  
     version: v1  
     metadata:  
     - name: connectionString  
       value: <your-azure-storage-queue-connection-string>  
     - name: queue  
       value: <your-queue-name>  
   ```  
   
2. Update the `image` field in the `keda.yaml` file with your registry's image:  
  
   ```  
   spec:  
     containers:  
     - name: whisperx  
       image: <your-registry>/<image-name>:latest  
   ```  
   
3. Apply the updated `keda.yaml` and `daprcomponent.yaml` files:  
  
   ```  
   kubectl apply -f keda.yaml  
   kubectl apply -f daprcomponent.yaml  
   ```  
   
## Usage  
   
1. Upload your audio files to the Azure Storage Queue specified in the `daprcomponent.yaml` file.  
   
2. The application will automatically scale based on the number of messages in the queue and process the audio files, transcribing them using Whisper.  
   
3. The transcriptions will be output with word-level timestamps and speaker diarization.  
   
## Troubleshooting  
   
- To check the logs of the WhisperX worker:  
  
  ```  
  kubectl logs -l app=whisperx -c whisperx  
  ```  
   
- To check the status of KEDA and Dapr components:  
  
  ```  
  kubectl get pods -n keda  
  kubectl get pods -n dapr-system  
  ```  
   
- If you encounter any issues, consider consulting the [KEDA documentation](https://keda.sh/docs/2.0/concepts/) or the [Dapr documentation](https://docs.dapr.io/getting-started/) for guidance.  
   